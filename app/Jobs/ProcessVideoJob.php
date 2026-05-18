<?php

namespace App\Jobs;

use App\Models\Video;
use App\Models\Clip;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

class ProcessVideoJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    protected $video;

    /**
     * The number of seconds the job can run before timing out.
     * Video processing takes time (especially local offline models), so we set a generous timeout.
     *
     * @var int
     */
    public $timeout = 1200; // 20 minutes

    /**
     * Create a new job instance.
     */
    public function __construct(Video $video)
    {
        $this->video = $video;
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        $video = $this->video;
        $video->update(['status' => 'processing']);

        try {
            // Setup directories
            $outputSubDir = "public/clipper/{$video->id}";
            $outputDirAbs = storage_path("app/{$outputSubDir}");
            if (!file_exists($outputDirAbs)) {
                mkdir($outputDirAbs, 0755, true);
            }

            // Retrieve configuration values
            $aiProvider = env('AI_PROVIDER', 'gemini');
            $ollamaModel = env('OLLAMA_MODEL', 'llama3');
            $whisperModel = env('WHISPER_MODEL', 'base');
            $ffmpegPath = env('FFMPEG_PATH', 'ffmpeg');
            $ytdlpPath = env('YT_DLP_PATH', 'yt-dlp');

            $geminiKey = env('GEMINI_API_KEY');
            if ($aiProvider === 'gemini' && empty($geminiKey)) {
                throw new \Exception("GEMINI_API_KEY is not configured in your .env file. Please get a free API key from Google AI Studio or change AI_PROVIDER to 'local' in your .env");
            }

            // Resolve video source input
            $sourceInput = "";
            if ($video->source_type === 'youtube') {
                $sourceInput = $video->source_url;
                $video->update(['status' => 'downloading']);
            } else {
                // Uploaded local video
                $sourceInput = storage_path("app/public/" . $video->file_path);
                if (!file_exists($sourceInput)) {
                    throw new \Exception("Source video file not found at: " . $sourceInput);
                }
            }

            // Construct python command
            $cliEnginePath = base_path('clipper.py');
            
            // Detect Python virtual environment automatically
            $pythonPath = 'python';
            $venvPathWin = base_path('.venv/Scripts/python.exe');
            $venvPathLinux = base_path('.venv/bin/python');
            
            if (file_exists($venvPathWin)) {
                $pythonPath = $venvPathWin;
            } elseif (file_exists($venvPathLinux)) {
                $pythonPath = $venvPathLinux;
            }
            
            $command = [
                $pythonPath,
                $cliEnginePath,
                '--source', $sourceInput,

                '--type', $video->source_type,
                '--output-dir', $outputDirAbs,
                '--provider', $aiProvider,
                '--ffmpeg-path', $ffmpegPath,
                '--ytdlp-path', $ytdlpPath
            ];

            if ($aiProvider === 'gemini') {
                $command[] = '--api-key';
                $command[] = $geminiKey;
            } else {
                $command[] = '--ollama-model';
                $command[] = $ollamaModel;
                $command[] = '--whisper-model';
                $command[] = $whisperModel;
            }

            Log::info("Running Video Clipper Python Engine ({$aiProvider}) for Video ID: {$video->id}", ['command' => $command]);


            $video->update(['status' => 'transcribing']); // Moving into transcription/moment processing

            $process = new Process($command);
            $process->setTimeout($this->timeout);
            $process->run();

            // Check if process completed successfully
            if (!$process->isSuccessful()) {
                throw new ProcessFailedException($process);
            }

            $output = $process->getOutput();
            Log::info("Python Clipper execution output captured for Video ID: {$video->id}");

            // Extract JSON from output markers
            $successJson = null;
            $errorJson = null;

            if (preg_match('/SUCCESS_MARKER_JSON_START\s*(.*?)\s*SUCCESS_MARKER_JSON_END/s', $output, $matches)) {
                $successJson = json_decode($matches[1], true);
            }

            if (preg_match('/ERROR_MARKER_JSON_START\s*(.*?)\s*ERROR_MARKER_JSON_END/s', $output, $matches)) {
                $errorJson = json_decode($matches[1], true);
            }

            if ($errorJson) {
                throw new \Exception($errorJson['error'] ?? 'Unknown error occurred in python clipper engine.');
            }

            if (!$successJson || !isset($successJson['clips'])) {
                Log::error("Failed to parse clipper JSON. Raw output: " . $output);
                throw new \Exception("Invalid JSON format returned from Clipper Engine.");
            }

            // Slicing and writing clips completed. Let's record them in the DB!
            $video->update(['status' => 'clipping']);

            // Update video title dynamically if it was left blank by the user
            if (isset($successJson['video_title']) && !empty($successJson['video_title'])) {
                if (empty($video->title) || str_starts_with($video->title, 'Video Clipper ')) {
                    $video->update(['title' => $successJson['video_title']]);
                }
            }

            // Save original title and youtube channel details
            if (isset($successJson['original_title']) && !empty($successJson['original_title'])) {
                $video->update(['original_title' => $successJson['original_title']]);
            }
            if (isset($successJson['youtube_channel']) && !empty($successJson['youtube_channel'])) {
                $video->update(['youtube_channel' => $successJson['youtube_channel']]);
            }

            // If youtube video, we can save its path in the database for reference
            if ($video->source_type === 'youtube' && isset($successJson['source_video_downloaded'])) {
                $relativeDownloadedPath = "clipper/{$video->id}/source_video.mp4";
                $video->update(['file_path' => $relativeDownloadedPath]);
            }

            // Save each clip
            foreach ($successJson['clips'] as $clipData) {
                Clip::create([
                    'video_id' => $video->id,
                    'title' => $clipData['title'],
                    'description' => $clipData['description'],
                    'file_path' => "clipper/{$video->id}/" . $clipData['clip_filename'],
                    'start_time' => $clipData['start_time'],
                    'end_time' => $clipData['end_time'],
                    'start_seconds' => $clipData['start_seconds'],
                    'end_seconds' => $clipData['end_seconds'],
                    'subtitles_srt' => $clipData['srt_content'],
                    'subtitles_vtt' => $clipData['vtt_content'],
                    'subtitles_dual' => $clipData['subtitles_dual']
                ]);
            }

            // Mark job as completed
            $video->update(['status' => 'completed']);
            Log::info("Successfully processed and generated clips for Video ID: {$video->id}");

        } catch (\Exception $e) {
            Log::error("Error processing Video ID: {$video->id}. Message: " . $e->getMessage());
            $video->update([
                'status' => 'failed',
                'error_message' => $e->getMessage()
            ]);
        }
    }
}

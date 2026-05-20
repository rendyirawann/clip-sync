<?php

namespace App\Http\Controllers\Backend;

use App\Http\Controllers\Controller;
use App\Models\Video;
use App\Models\Clip;
use App\Jobs\ProcessGameVideoJob;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Log;

class GameVideoClipperController extends Controller
{
    /**
     * Display a listing of the videos.
     */
    public function index()
    {
        $videos = Video::where('clipper_type', 'game')
            ->withCount('clips')
            ->latest()
            ->paginate(10);

        // Scan storage/app/public/bgm/phonk for .mp3 tracks
        $bgmFolder = storage_path('app/public/bgm/phonk');
        $bgmTracks = [];
        if (file_exists($bgmFolder)) {
            $files = scandir($bgmFolder);
            foreach ($files as $file) {
                if (pathinfo($file, PATHINFO_EXTENSION) === 'mp3') {
                    $bgmTracks[] = $file;
                }
            }
        }

        return view('backend.game_clipper.index', compact('videos', 'bgmTracks'));
    }

    /**
     * Store a newly created video in storage and dispatch processing job.
     */
    public function store(Request $request)
    {
        $request->validate([
            'source_type' => 'required|in:upload,youtube',
            'title' => 'nullable|string|max:255',
            'youtube_url' => 'required_if:source_type,youtube|nullable|url',
            'video_file' => 'required_if:source_type,upload|nullable|file|mimes:mp4,mov,avi,mkv|max:102400', // 100MB max
            'clip_count' => 'nullable|integer|min:1|max:10',
            'duration' => 'nullable|integer|in:30,60,90,120,180,360',
            'watermark' => 'nullable|string|max:100',
            'provider' => 'nullable|in:gemini,local',
            'model' => 'nullable|string|max:100',
            'custom_model' => 'nullable|string|max:100',
            'orientation' => 'nullable|in:16:9,9:16',
            'engine_mode' => 'nullable|in:standard,opsi_a,opsi_b',
            'burn_subtitles' => 'nullable|boolean',
            'bgm_type' => 'required|in:none,local,youtube',
            'bgm_local_track' => 'required_if:bgm_type,local|nullable|string',
            'bgm_youtube_url' => 'required_if:bgm_type,youtube|nullable|url',
        ], [
            'youtube_url.required_if' => 'Kolom Link YouTube harus diisi jika tipe sumber adalah YouTube.',
            'video_file.required_if' => 'File video harus diunggah jika tipe sumber adalah Upload PC.',
            'video_file.max' => 'Ukuran video maksimal adalah 100MB.',
            'video_file.mimes' => 'Format video yang didukung adalah MP4, MOV, AVI, dan MKV.',
            'clip_count.max' => 'Jumlah maksimal klip yang diizinkan adalah 10.',
            'duration.in' => 'Durasi klip yang dipilih tidak valid.',
            'bgm_local_track.required_if' => 'Anda harus memilih salah satu musik Phonk dari folder.',
            'bgm_youtube_url.required_if' => 'Kolom Link YouTube BGM harus diisi.',
            'bgm_youtube_url.url' => 'Format link YouTube BGM tidak valid.'
        ]);

        try {
            $video = new Video();
            $video->user_id = auth()->id();
            $video->title = $request->title ?: 'Gaming Highlight ' . date('Y-m-d H:i');
            $video->source_type = $request->source_type;
            $video->clip_count = $request->clip_count ?: 3;
            
            // Map target duration dropdown
            $duration = (int)($request->duration ?: 90);
            switch ($duration) {
                case 30:
                     $min = 20; $max = 40; break;
                case 60:
                     $min = 45; $max = 75; break;
                case 90:
                     $min = 70; $max = 110; break;
                case 120:
                     $min = 90; $max = 140; break;
                case 180:
                     $min = 140; $max = 220; break;
                case 360:
                     $min = 300; $max = 420; break;
                default:
                     $min = 30; $max = 90; break;
            }
            $video->clip_duration_min = $min;
            $video->clip_duration_max = $max;
            $video->watermark = $request->watermark;
            $video->orientation = $request->orientation ?: '16:9';
            $video->is_podcast = false; // Always false for gaming edits
            $video->engine_mode = $request->engine_mode ?: 'standard';
            $video->burn_subtitles = $request->has('burn_subtitles') ? (bool)$request->burn_subtitles : false;
            
            // Clipper metadata columns
            $video->clipper_type = 'game';
            $video->bgm_type = $request->bgm_type;
            if ($request->bgm_type === 'local') {
                $video->bgm_track = $request->bgm_local_track;
            } elseif ($request->bgm_type === 'youtube') {
                $video->bgm_track = $request->bgm_youtube_url;
            } else {
                $video->bgm_track = null;
            }

            // Set dynamically AI provider and model from request
            $video->provider = $request->provider ?: 'gemini';
            if ($video->provider === 'gemini') {
                $video->model = 'Gemini 1.5 Flash';
            } else {
                $video->model = $request->model === 'custom' 
                    ? ($request->custom_model ?: 'llama3') 
                    : ($request->model ?: 'llama3');
            }
            
            $video->status = 'pending';

            if ($request->source_type === 'youtube') {
                $video->source_url = $request->youtube_url;
            } else {
                // Local PC Upload
                if ($request->hasFile('video_file')) {
                    $file = $request->file('video_file');
                    $filename = time() . '_' . uniqid() . '.' . $file->getClientOriginalExtension();
                    
                    // Save in storage/app/public/clipper/uploads
                    $path = $file->storeAs('clipper/uploads', $filename, 'public');
                    $video->file_path = $path;
                } else {
                    return redirect()->back()->with('error', 'Gagal mengunggah video. File tidak ditemukan.');
                }
            }

            $video->save();

            // Dispatch background job
            ProcessGameVideoJob::dispatch($video);

            return redirect()->route('game-clipper.index')->with('success', 'Video game berhasil dikirim! Proses auto-clipping dan mix Phonk BGM sedang berjalan di background.');

        } catch (\Exception $e) {
            Log::error('Error storing game clipper video: ' . $e->getMessage());
            return redirect()->back()->with('error', 'Terjadi kesalahan: ' . $e->getMessage());
        }
    }

    /**
     * Display the specified video and its clips.
     */
    public function show($id)
    {
        $video = Video::where('clipper_type', 'game')->with('clips')->findOrFail($id);
        return view('backend.game_clipper.show', compact('video'));
    }

    /**
     * Remove the specified video and associated files from storage.
     */
    public function destroy($id)
    {
        $video = Video::where('clipper_type', 'game')->findOrFail($id);

        try {
            // Delete source upload file if any
            if ($video->source_type === 'upload' && $video->file_path) {
                Storage::disk('public')->delete($video->file_path);
            }

            // Delete processing directory inside public/clipper/{id}
            $clipperDir = "clipper/{$video->id}";
            if (Storage::disk('public')->exists($clipperDir)) {
                Storage::disk('public')->deleteDirectory($clipperDir);
            }

            $video->delete();

            return redirect()->route('game-clipper.index')->with('success', 'Video game dan kliping terkait berhasil dihapus.');

        } catch (\Exception $e) {
            Log::error('Error deleting game video clipper files: ' . $e->getMessage());
            return redirect()->route('game-clipper.index')->with('error', 'Gagal menghapus file: ' . $e->getMessage());
        }
    }

    /**
     * Update dynamic clip metadata and dual subtitle files.
     */
    public function updateClip(Request $request, $id)
    {
        $clip = Clip::findOrFail($id);
        $video = $clip->video;

        $request->validate([
            'title' => 'required|string|max:255',
            'description' => 'nullable|string',
            'subtitles' => 'nullable|array',
        ]);

        // Update Title & Description/Caption
        $clip->title = $request->title;

        // Auto-inject hashtags if they are missing
        $caption = $request->description ?: '';
        if (!str_contains($caption, '#')) {
            $caption .= "\n\n#fyp #videoclipper #viral #highlight #gaming #phonk";
        }
        $clip->description = $caption;

        // Update Subtitles if provided
        if ($request->has('subtitles')) {
            $clip->subtitles_dual = $request->subtitles;

            // Re-generate .srt and .vtt files on disk
            $filePath = $clip->file_path; // e.g. "clipper/9/clip_1.mp4"
            $subPathVtt = str_replace('.mp4', '_sub.vtt', $filePath);
            $subPathSrt = str_replace('.mp4', '_sub.srt', $filePath);

            $outputFileVtt = storage_path("app/public/" . $subPathVtt);
            $outputFileSrt = storage_path("app/public/" . $subPathSrt);

            $srtLines = [];
            $vttLines = ["WEBVTT\n"];
            $index = 1;

            foreach ($request->subtitles as $sub) {
                $startSec = (float)($sub['start_seconds'] ?? 0);
                $endSec = (float)($sub['end_seconds'] ?? 0);
                $textId = $sub['text_id'] ?? '';
                $textEn = $sub['text_en'] ?? '';

                $text = $textId ?: $textEn;
                if ($textEn && $textId && $textEn !== $textId) {
                    $text = "{$textEn}\n{$textId}";
                }

                // SRT formatting
                $srtLines[] = $index;
                $srtLines[] = $this->formatSrtTimestamp($startSec) . " --> " . $this->formatSrtTimestamp($endSec);
                $srtLines[] = $text . "\n";

                // VTT formatting
                $vttLines[] = $index;
                $vttLines[] = $this->formatVttTimestamp($startSec) . " --> " . $this->formatVttTimestamp($endSec);
                $vttLines[] = $text . "\n";

                $index++;
            }

            file_put_contents($outputFileSrt, implode("\n", $srtLines));
            file_put_contents($outputFileVtt, implode("\n", $vttLines));
        }

        $clip->save();

        return response()->json([
            'success' => true,
            'message' => 'Klip dan subtitle berhasil diperbarui!',
            'clip' => $clip
        ]);
    }

    /**
     * Format seconds to SRT subtitle timestamp format.
     */
    private function formatSrtTimestamp($seconds)
    {
        $hours = floor($seconds / 3600);
        $minutes = floor(($seconds % 3600) / 60);
        $secs = floor($seconds % 60);
        $ms = round(($seconds - floor($seconds)) * 1000);
        return sprintf('%02d:%02d:%02d,%03d', $hours, $minutes, $secs, $ms);
    }

    /**
     * Format seconds to WebVTT subtitle timestamp format.
     */
    private function formatVttTimestamp($seconds)
    {
        $hours = floor($seconds / 3600);
        $minutes = floor(($seconds % 3600) / 60);
        $secs = floor($seconds % 60);
        $ms = round(($seconds - floor($seconds)) * 1000);
        return sprintf('%02d:%02d:%02d.%03d', $hours, $minutes, $secs, $ms);
    }

    /**
     * Stream the original/source video file supporting HTTP Range requests.
     */
    public function streamVideoSource($id)
    {
        $video = Video::where('clipper_type', 'game')->findOrFail($id);
        $path = storage_path("app/public/" . $video->file_path);

        return $this->streamFileWithRange($path);
    }

    /**
     * Stream a clip video file supporting HTTP Range requests.
     */
    public function streamClip($id)
    {
        $clip = Clip::findOrFail($id);
        $path = storage_path("app/public/" . $clip->file_path);

        return $this->streamFileWithRange($path);
    }

    /**
     * Core range-based file streaming handler (supports HTTP 206 Partial Content).
     */
    private function streamFileWithRange($path)
    {
        if (!file_exists($path)) {
            abort(404, "File video tidak ditemukan.");
        }

        $stream = fopen($path, 'rb');
        $size   = filesize($path);
        $length = $size;
        $start  = 0;
        $end    = $size - 1;

        $headers = [
            'Content-Type' => 'video/mp4',
            'Accept-Ranges' => 'bytes',
        ];

        if (request()->headers->has('Range')) {
            $range = request()->header('Range');
            if (preg_match('/bytes=\s*(\d+)-(\d*)/', $range, $matches)) {
                $start = (int)$matches[1];
                if (!empty($matches[2])) {
                    $end = (int)$matches[2];
                }
            }

            $length = $end - $start + 1;
            fseek($stream, $start);
            
            $headers['Content-Range'] = "bytes $start-$end/$size";
            
            return response()->stream(function () use ($stream, $length) {
                $bufferSize = 8192;
                $bytesLeft = $length;
                while ($bytesLeft > 0 && !connection_aborted()) {
                    $bytesToRead = min($bufferSize, $bytesLeft);
                    $data = fread($stream, $bytesToRead);
                    echo $data;
                    flush();
                    $bytesLeft -= strlen($data);
                }
                fclose($stream);
            }, 206, $headers);
        }

        $headers['Content-Length'] = $size;

        return response()->stream(function () use ($stream) {
            fpassthru($stream);
            fclose($stream);
        }, 200, $headers);
    }
}

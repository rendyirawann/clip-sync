<?php

namespace App\Http\Controllers\Backend;

use App\Http\Controllers\Controller;
use App\Models\Video;
use App\Models\Clip;
use App\Jobs\ProcessVideoJob;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Log;

class VideoClipperController extends Controller
{
    /**
     * Display a listing of the videos.
     */
    public function index()
    {
        $videos = Video::withCount('clips')
            ->latest()
            ->paginate(10);

        return view('backend.clipper.index', compact('videos'));
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
        ], [
            'youtube_url.required_if' => 'Kolom Link YouTube harus diisi jika tipe sumber adalah YouTube.',
            'video_file.required_if' => 'File video harus diunggah jika tipe sumber adalah Upload PC.',
            'video_file.max' => 'Ukuran video maksimal adalah 100MB.',
            'video_file.mimes' => 'Format video yang didukung adalah MP4, MOV, AVI, dan MKV.',
            'clip_count.max' => 'Jumlah maksimal klip yang diizinkan adalah 10.',
            'duration.in' => 'Durasi klip yang dipilih tidak valid.'
        ]);

        try {
            $video = new Video();
            $video->user_id = auth()->id();
            $video->title = $request->title ?: 'Video Clipper ' . date('Y-m-d H:i');
            $video->source_type = $request->source_type;
            $video->clip_count = $request->clip_count ?: 3;
            
            // Map selected target duration dropdown to optimal min & max ranges for the AI slicing algorithm
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
            
            // Set dynamic AI provider and model from request
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
            ProcessVideoJob::dispatch($video);

            return redirect()->route('clipper.index')->with('success', 'Video berhasil dikirim! Sistem sedang memproses kliping di background.');

        } catch (\Exception $e) {
            Log::error('Error storing clipper video: ' . $e->getMessage());
            return redirect()->back()->with('error', 'Terjadi kesalahan: ' . $e->getMessage());
        }
    }

    /**
     * Display the specified video and its clips.
     */
    public function show($id)
    {
        $video = Video::with('clips')->findOrFail($id);
        return view('backend.clipper.show', compact('video'));
    }

    /**
     * Remove the specified video and associated files from storage.
     */
    public function destroy($id)
    {
        $video = Video::findOrFail($id);

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

            return redirect()->route('clipper.index')->with('success', 'Video dan kliping terkait berhasil dihapus.');

        } catch (\Exception $e) {
            Log::error('Error deleting video clipper files: ' . $e->getMessage());
            return redirect()->route('clipper.index')->with('error', 'Gagal menghapus file: ' . $e->getMessage());
        }
    }
}

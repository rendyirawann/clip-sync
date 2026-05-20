@extends('backend.layout.app')
@section('title', 'Hasil Game & Anime Video Clipper 🎮✨')

@section('content')
<div class="mt-5 mb-10 container-fluid">
    <!-- Breadcrumbs & Navigation -->
    <div class="d-flex align-items-center justify-content-between mb-8 flex-wrap gap-4">
        <div>
            <ul class="breadcrumb breadcrumb-separatorless fw-semibold fs-7 my-1">
                <li class="breadcrumb-item text-muted">
                    <a href="{{ route('game-clipper.index') }}" class="text-muted text-hover-primary">Game & Anime Clipper</a>
                </li>
                <li class="breadcrumb-item">
                    <span class="bullet bg-gray-500 w-5px h-2px"></span>
                </li>
                <li class="breadcrumb-item text-gray-900">Detail Project</li>
            </ul>
            <h1 class="text-gray-900 fw-bold fs-1 mt-2">Detail Game Clipper: {{ $video->title }} 🎮</h1>
            @if(!empty($video->original_title) && $video->original_title !== $video->title)
                <span class="text-muted fs-6 fw-semibold d-block mt-1">
                    Original: <span class="fst-italic text-gray-700 fw-bold">{{ $video->original_title }}</span>
                </span>
            @endif
        </div>
        <div>
            <a href="{{ route('game-clipper.index') }}" class="btn d-flex align-items-center" style="color: #6366f1; background-color: rgba(99, 102, 241, 0.1);">
                <i class="ki-duotone ki-left-square fs-3 me-2" style="color: #6366f1;"><span class="path1"></span><span class="path2"></span></i>
                Kembali ke Dashboard
            </a>
        </div>
    </div>

    <!-- Main Project Info Row -->
    <div class="row g-10 mb-10">
        <!-- Original Video Details -->
        <div class="col-xl-4 col-lg-5">
            <div class="card shadow-sm border-0 h-100 bg-white">
                <div class="card-header border-0 pt-7">
                    <h3 class="card-title fw-bold text-gray-900 fs-3">Video Sumber</h3>
                </div>
                <div class="card-body">
                    <!-- Original Video Player -->
                    <div class="mb-6 rounded overflow-hidden shadow-sm bg-dark position-relative" style="aspect-ratio: 16/9;">
                        @if($video->file_path)
                            <video controls class="w-100 h-100" style="object-fit: contain;">
                                <source src="{{ route('game-clipper.stream-source', $video->id) }}" type="video/mp4">
                                Browser Anda tidak mendukung HTML5 video.
                            </video>
                        @else
                            <div class="d-flex flex-column align-items-center justify-content-center h-100 text-white p-5 bg-dark">
                                <i class="fab fa-youtube text-danger fs-3x mb-3"></i>
                                <span class="fw-bold">YouTube Video</span>
                                <a href="{{ $video->source_url }}" target="_blank" class="text-primary fs-8 text-center mt-2 truncate-2-lines">{{ $video->source_url }}</a>
                            </div>
                        @endif
                    </div>

                    <!-- Metadata List -->
                    <div class="separator separator-dashed mb-6"></div>
                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Sumber</span>
                        <div class="d-flex align-items-center mt-1">
                            @if($video->source_type === 'youtube')
                                <span class="badge badge-light-danger px-3 py-1 fs-8 me-2">YouTube</span>
                                <a href="{{ $video->source_url }}" target="_blank" class="text-gray-800 text-hover-primary fs-7 fw-bold text-truncate" style="max-width: 200px;">Buka di YouTube 🔗</a>
                            @else
                                <span class="badge px-3 py-1 fs-8 me-2" style="color: #6366f1; background-color: rgba(99, 102, 241, 0.1);">Upload PC</span>
                                <span class="text-gray-800 fs-7 fw-bold">File Lokal</span>
                            @endif
                        </div>
                    </div>
                    
                    @if($video->source_type === 'youtube' && !empty($video->youtube_channel))
                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Channel YouTube</span>
                        <span class="text-gray-800 fs-7 fw-bold d-block mt-1">
                            <i class="fab fa-youtube text-danger me-1"></i> {{ $video->youtube_channel }}
                        </span>
                    </div>
                    @endif

                    @if(!empty($video->original_title) && $video->original_title !== $video->title)
                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Judul Asli</span>
                        <span class="text-gray-800 fs-7 fw-semibold d-block mt-1 lh-sm">
                            {{ $video->original_title }}
                        </span>
                    </div>
                    @endif

                    <!-- Phonk BGM Info -->
                    @if($video->bgm_type !== 'none' && !empty($video->bgm_track))
                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Background Music (BGM Phonk) 🎧🔥</span>
                        <span class="text-gray-800 fs-7 fw-bold d-block mt-1">
                            @if($video->bgm_type === 'youtube')
                                <span class="badge badge-light-danger border border-danger border-dashed px-3 py-1 fs-8 text-danger me-2">
                                    <i class="fab fa-youtube text-danger me-1"></i> YouTube BGM
                                </span>
                                <a href="{{ $video->bgm_track }}" target="_blank" class="text-primary fs-8 text-truncate d-inline-block align-middle mt-1" style="max-width: 180px;">{{ $video->bgm_track }}</a>
                            @else
                                <span class="badge border border-indigo border-dashed px-3 py-1 fs-8 me-2" style="color: #6366f1; border-color: #6366f1 !important; background-color: rgba(99, 102, 241, 0.05);">
                                    <i class="ki-duotone ki-music text-primary me-1" style="color: #6366f1 !important;"><span class="path1"></span><span class="path2"></span></i> Folder Phonk
                                </span>
                                <span class="text-gray-800 fs-8 fw-bold">{{ ucwords(str_replace(['_', '.mp3'], [' ', ''], $video->bgm_track)) }}</span>
                            @endif
                        </span>
                    </div>
                    @endif

                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Selesai Diproses</span>
                        <span class="text-gray-800 fs-7 fw-bold d-block mt-1">{{ $video->updated_at->timezone('Asia/Jakarta')->format('d F Y - H:i T') }}</span>
                    </div>

                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Mesin Pemroses</span>
                        <span class="text-gray-800 fs-7 fw-bold d-block mt-1">
                            @if(($video->provider ?? 'gemini') === 'local')
                                <span class="badge badge-light-warning border border-warning border-dashed px-3 py-1 fs-8 text-warning me-2" data-bs-toggle="tooltip" title="Offline AI Engine (Whisper + Ollama)">
                                    <i class="ki-duotone ki-home-trend-up fs-6 text-warning me-1"><span class="path1"></span><span class="path2"></span></i> Local ({{ $video->model ?? 'Ollama' }})
                                </span>
                            @else
                                <span class="badge badge-light-success border border-success border-dashed px-3 py-1 fs-8 text-success me-2" data-bs-toggle="tooltip" title="Cloud AI Engine (Google Gemini)">
                                    <i class="ki-duotone ki-electricity fs-6 text-success me-1"><span class="path1"></span><span class="path2"></span></i> {{ $video->model ?? 'Gemini 1.5 Flash' }}
                                </span>
                            @endif
                            <span class="badge border border-indigo border-dashed px-3 py-1 fs-8" style="color: #6366f1; border-color: #6366f1 !important; background-color: rgba(99, 102, 241, 0.05);">
                                <i class="ki-duotone ki-briefcase fs-6 me-1" style="color: #6366f1 !important;"><span class="path1"></span><span class="path2"></span></i> FFmpeg
                            </span>
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Clips Showcase Grid (Right) -->
        <div class="col-xl-8 col-lg-7">
            <div class="card shadow-sm border-0 h-100 bg-white">
                <div class="card-header border-0 pt-7">
                    <h3 class="card-title align-items-start flex-column">
                        <span class="card-label fw-bold text-gray-900 fs-3 mb-1">Hasil Generasi Klip Highlights & Phonk BGM 🎮🔥</span>
                        <span class="text-muted fw-semibold fs-7">Sistem berhasil memotong klip video terbaik dengan reframer cerdas dan mixing Phonk BGM.</span>
                    </h3>
                </div>

                <div class="card-body">
                    <!-- Carousel Slide Mode / Grid Mode -->
                    <div class="row g-8">
                        @foreach($video->clips as $clip)
                            <div class="col-md-6 col-xl-12">
                                <div class="card border border-gray-200 shadow-none hover-shadow-sm transition-all mb-4">
                                    <div class="row g-0 align-items-stretch">
                                        <!-- Player Column -->
                                        <div class="col-xl-6 bg-dark rounded-start overflow-hidden d-flex align-items-center justify-content-center position-relative" style="min-height: 250px;">
                                            <!-- Floating Live Slicing Timer Card -->
                                            <div class="position-absolute top-0 start-0 m-4 p-3 rounded bg-dark bg-opacity-75 text-white fs-8 fw-semibold border border-indigo border-opacity-10 shadow d-flex flex-column gap-1" style="z-index: 10; backdrop-filter: blur(4px);">
                                                <div class="d-flex align-items-center">
                                                    <span class="bullet bullet-dot bg-danger h-8px w-8px pulse-red me-2"></span>
                                                    <span>Slicing Timer: <span id="timer_stopwatch_{{ $clip->id }}" class="text-warning">00:00</span></span>
                                                </div>
                                                <div class="text-white-50 fs-9 d-flex align-items-center mt-1">
                                                    <i class="ki-duotone ki-time fs-8 text-primary me-1.5"><span class="path1"></span><span class="path2"></span></i>
                                                    <span>Waktu Asli: <span id="timer_absolute_{{ $clip->id }}" class="text-success">{{ $clip->start_time }}</span></span>
                                                </div>
                                            </div>

                                            <video id="player_{{ $clip->id }}" data-start-seconds="{{ $clip->start_seconds }}" controls class="w-100 h-100" style="object-fit: contain;" crossorigin="anonymous">
                                                <source src="{{ route('game-clipper.stream-clip', $clip->id) }}" type="video/mp4">
                                                <!-- Dual Subtitles Track -->
                                                @php
                                                    $subVttPath = str_replace('.mp4', '_sub.vtt', $clip->file_path);
                                                @endphp
                                                @if(!($video->burn_subtitles ?? true))
                                                    <track src="/storage/{{ $subVttPath }}" kind="subtitles" srclang="id" label="Indo-En Dual Sub" default>
                                                @else
                                                    <track src="/storage/{{ $subVttPath }}" kind="subtitles" srclang="id" label="Indo-En Dual Sub">
                                                @endif
                                                Browser Anda tidak mendukung HTML5 video.
                                            </video>
                                        </div>

                                        <!-- Clip details Column -->
                                        <div class="col-xl-6 d-flex flex-column justify-content-between p-6">
                                            <div>
                                                <!-- Title & Badge -->
                                                <div class="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
                                                    <span class="badge fw-bold px-3 py-1 fs-8" style="color: #6366f1; background-color: rgba(99, 102, 241, 0.1);">Klip #{{ $loop->iteration }}</span>
                                                    <span class="text-muted fs-8 fw-semibold">⏱️ {{ $clip->start_time }} - {{ $clip->end_time }}</span>
                                                </div>
                                                
                                                <!-- Caption Mockup Box (Draft Post) -->
                                                <div class="bg-light rounded p-4 mb-4 border border-gray-200 position-relative">
                                                    <span class="badge badge-light-dark fw-bold fs-9 px-2 py-1 position-absolute end-0 top-0 mt-3 me-3">Ready to Post 🎮</span>
                                                    
                                                    <span class="text-gray-600 fw-bold fs-9 d-block mb-1 text-uppercase tracking-wider">Judul Video:</span>
                                                    <h4 class="text-gray-900 fw-bold fs-6 mb-3 clip-title-text">{{ $clip->title }}</h4>
                                                    
                                                    <span class="text-gray-600 fw-bold fs-9 d-block mb-1 text-uppercase tracking-wider">Caption & Hashtags (FYP):</span>
                                                    <p class="text-gray-800 fs-7 mb-0 lh-base clip-desc-text" style="white-space: pre-line;">{{ $clip->description }}@if($video->source_type === 'youtube' && !empty($video->youtube_channel))


📌 Source: {{ $video->source_url }}
🎥 Channel: {{ $video->youtube_channel }}@endif</p>
                                                    
                                                    <div class="mt-4 pt-3 border-top border-gray-200 d-flex justify-content-end">
                                                        <button type="button" class="btn btn-light-warning btn-sm py-2 px-3 d-inline-flex align-items-center fw-bold fs-8 me-2 edit-clip-btn"
                                                                data-clip-id="{{ $clip->id }}"
                                                                data-clip-title="{{ $clip->title }}"
                                                                data-clip-desc="{{ $clip->description }}"
                                                                data-clip-subs="{{ json_encode($clip->subtitles_dual) }}">
                                                            <i class="ki-duotone ki-notepad-edit fs-6 me-1.5"><span class="path1"></span><span class="path2"></span></i>
                                                            Edit Klip & Subtitle
                                                        </button>
                                                        <button type="button" class="btn btn-sm py-2 px-3 d-inline-flex align-items-center fw-bold fs-8" style="color: #6366f1; background-color: rgba(99, 102, 241, 0.1);" onclick="copyCaption(this)">
                                                            <i class="ki-duotone ki-copy fs-6 me-1.5" style="color: #6366f1;"><span class="path1"></span><span class="path2"></span></i>
                                                            Salin Judul & Caption
                                                        </button>
                                                    </div>
                                                </div>

                                                <!-- Interactive Transcript Box -->
                                                <div class="transcript-wrapper mb-4">
                                                    <span class="text-gray-800 fw-bold fs-8 d-block mb-2">📜 Transkrip & Subtitle (Klik Baris untuk Jump):</span>
                                                    <div class="transcript-box border border-dashed rounded p-3 bg-light-light overflow-auto" style="max-height: 120px;">
                                                        @if($clip->subtitles_dual && is_array($clip->subtitles_dual))
                                                            @foreach($clip->subtitles_dual as $sub)
                                                                <div class="transcript-line py-1 border-bottom border-gray-100 cursor-pointer hover-text-indigo fs-8 text-gray-700" 
                                                                     onclick="jumpToTime('player_{{ $clip->id }}', {{ $sub['start_seconds'] }})">
                                                                    <span class="fw-semibold me-2" style="color: #6366f1;">[{{ sprintf('%02d:%02d', floor($sub['start_seconds'] / 60), $sub['start_seconds'] % 60) }}]</span>
                                                                    @if(!empty($sub['text_en']) && $sub['text_en'] !== $sub['text_id'])
                                                                        <span>{{ $sub['text_en'] }} <br><span class="text-muted font-italic">{{ $sub['text_id'] }}</span></span>
                                                                    @else
                                                                        <span>{{ $sub['text_id'] }}</span>
                                                                    @endif
                                                                </div>
                                                            @endforeach
                                                        @else
                                                            <span class="text-muted fs-8">Transkrip tidak tersedia dalam bentuk data terstruktur.</span>
                                                        @endif
                                                    </div>
                                                </div>
                                            </div>

                                            <!-- Download and Actions -->
                                            <div class="d-flex align-items-center gap-3 pt-3 border-top border-gray-100">
                                                <a href="/storage/{{ $clip->file_path }}" download class="btn btn-sm w-100 py-3 d-flex align-items-center justify-content-center fw-bold text-white shadow-sm" style="background-color: #6366f1 !important; border-color: #6366f1 !important;">
                                                    <i class="ki-duotone ki-cloud-download fs-5 me-2"><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span></i>
                                                    Download Klip (.MP4)
                                                </a>
                                                <a href="/storage/clipper/{{ $video->id }}/clip_{{ $loop->iteration }}_sub.srt" download class="btn btn-sm btn-light-indigo py-3 px-4" data-bs-toggle="tooltip" title="Download Subtitle SRT" style="color: #6366f1; background-color: rgba(99, 102, 241, 0.1);">
                                                    SRT
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        @endforeach
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal Edit Klip & Subtitle -->
<div class="modal fade" id="modal_edit_clip" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content rounded-4 border-0 shadow-lg">
            <div class="modal-header border-0 bg-light py-5">
                <h3 class="modal-title fw-bold text-gray-900 fs-3 d-flex align-items-center">
                    <i class="ki-duotone ki-notepad-edit text-warning fs-1 me-2"><span class="path1"></span><span class="path2"></span></i>
                    Edit Judul, Caption & Subtitle Klip 📝
                </h3>
                <div class="btn btn-icon btn-sm btn-active-light-indigo ms-2" data-bs-dismiss="modal" aria-label="Close">
                    <i class="ki-duotone ki-cross fs-1"><span class="path1"></span><span class="path2"></span></i>
                </div>
            </div>
            
            <form id="form_edit_clip" onsubmit="submitEditClipForm(event)">
                @csrf
                <input type="hidden" id="edit_clip_id">
                
                <div class="modal-body py-8 px-lg-10 overflow-auto" style="max-height: 60vh;">
                    <!-- Title Input -->
                    <div class="fv-row mb-6">
                        <label class="required fs-6 fw-bold mb-2">Judul Klip (Viral Title)</label>
                        <input type="text" class="form-control form-control-solid rounded" id="edit_clip_title" required placeholder="Masukkan judul klip yang menarik...">
                    </div>
                    
                    <!-- Description / Caption Input -->
                    <div class="fv-row mb-6">
                        <label class="fs-6 fw-bold mb-2">Caption & Hashtags (TikTok / IG FYP Ready)</label>
                        <textarea class="form-control form-control-solid rounded" id="edit_clip_desc" rows="4" placeholder="Tulis caption Anda... #fyp dan tagar akan ditambahkan otomatis jika kosong!"></textarea>
                        <span class="form-text text-muted fs-8">💡 Tips: Tagar (#) akan disisipkan di akhir secara otomatis untuk memaksimalkan performa algoritma FYP jika Anda mengosongkannya.</span>
                    </div>
                    
                    <div class="separator separator-dashed my-6"></div>
                    
                    <!-- Subtitles Scroll List -->
                    <div class="mb-4">
                        <label class="fs-6 fw-bold mb-2 d-block">📜 Teks Transkrip & Subtitle Video (Bisa Diedit Langsung!):</label>
                        <span class="text-muted fs-8 d-block mb-4">Mengedit teks di bawah ini akan memperbarui file subtitle `.srt` & `.vtt` pemutar video secara instan!</span>
                        
                        <div id="subtitles_edit_list" class="border border-dashed rounded p-4 bg-light bg-opacity-50 overflow-auto" style="max-height: 250px;">
                            <!-- Dinamis baris-baris subtitle diisi dari JS -->
                        </div>
                    </div>
                </div>
                
                <div class="modal-footer border-0 bg-light py-5 d-flex justify-content-end gap-3">
                    <button type="button" class="btn btn-light rounded" data-bs-dismiss="modal">Batal</button>
                    <button type="submit" class="btn rounded d-flex align-items-center fw-bold text-white" id="btn_save_clip_changes" style="background-color: #6366f1; border-color: #6366f1;">
                        <i class="ki-duotone ki-disk fs-4 me-2"><span class="path1"></span><span class="path2"></span></i>
                        Simpan Perubahan & Update Video
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<style>
/* CSS styles for show blade */
.transcript-box {
    max-height: 120px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #dbdfe9 transparent;
}
.transcript-box::-webkit-scrollbar {
    width: 4px;
}
.transcript-box::-webkit-scrollbar-track {
    background: transparent;
}
.transcript-box::-webkit-scrollbar-thumb {
    background-color: #dbdfe9;
    border-radius: 4px;
}
.transcript-line {
    transition: all 0.15s ease-in-out;
}
.transcript-line:hover {
    background-color: rgba(99, 102, 241, 0.05);
    padding-left: 4px;
}
.hover-text-indigo:hover {
    color: #6366f1 !important;
}
.truncate-3-lines {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;  
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Style HTML5 video subtitles (cues) */
video::cue {
    color: #ffeb3b !important; /* Premium Yellow */
    background-color: rgba(0, 0, 0, 0.75) !important; /* Semi-transparent black background */
    font-size: 1.1rem !important;
    font-weight: bold !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.5 !important;
}

/* Pulsing Red Dot Animation */
@keyframes pulse-red {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(241, 65, 108, 0.7);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 5px rgba(241, 65, 108, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(241, 65, 108, 0);
    }
}
.pulse-red {
    box-shadow: 0 0 0 0 rgba(241, 65, 108, 0.7);
    animation: pulse-red 2s infinite;
    border-radius: 50%;
}
</style>

<script>
// Javascript to jump to specific seconds in player
function jumpToTime(playerId, seconds) {
    const video = document.getElementById(playerId);
    if (video) {
        video.currentTime = seconds;
        video.play();
        
        // Scroll video player into view smoothly
        video.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Premium click-to-copy social media caption and hashtags helper
function copyCaption(button) {
    const card = button.closest('.bg-light');
    if (!card) return;
    
    const titleEl = card.querySelector('.clip-title-text');
    const descEl = card.querySelector('.clip-desc-text');
    
    if (!titleEl || !descEl) return;
    
    const title = titleEl.innerText ? titleEl.innerText.trim() : '';
    const description = descEl.innerText ? descEl.innerText.trim() : '';
    
    const textToCopy = `Judul: ${title}\n\n${description}`;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Success button feedback
        const originalHtml = button.innerHTML;
        button.innerHTML = '<i class="ki-duotone ki-check fs-6 me-1.5"><span class="path1"></span></i>Tersalin!';
        button.style.backgroundColor = '#10b981';
        button.style.color = '#ffffff';
        
        // SweetAlert2 Toast pop up
        if (typeof Swal !== 'undefined') {
            const Toast = Swal.mixin({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2500,
                timerProgressBar: true
            });
            Toast.fire({
                icon: 'success',
                title: 'Judul, Caption & Hashtag disalin!'
            });
        }
        
        setTimeout(() => {
            button.innerHTML = originalHtml;
            button.style.backgroundColor = 'rgba(99, 102, 241, 0.1)';
            button.style.color = '#6366f1';
        }, 2500);
    }).catch(err => {
        console.error('Gagal menyalin text: ', err);
    });
}

// Dynamic Stopwatch & Original Cut Time Sync
document.addEventListener('DOMContentLoaded', function() {
    const players = document.querySelectorAll('video');
    players.forEach(video => {
        if (!video.id.startsWith('player_')) return;
        
        const clipId = video.id.replace('player_', '');
        const stopwatchSpan = document.getElementById(`timer_stopwatch_${clipId}`);
        const absoluteSpan = document.getElementById(`timer_absolute_${clipId}`);
        
        video.addEventListener('timeupdate', function() {
            const startSec = parseFloat(video.getAttribute('data-start-seconds')) || 0;
            const currentTime = video.currentTime;
            
            // 1. Format stopwatch time (MM:SS)
            const stopwatchSecs = Math.floor(currentTime);
            const stopMins = Math.floor(stopwatchSecs / 60);
            const stopSecs = stopwatchSecs % 60;
            if (stopwatchSpan) {
                stopwatchSpan.innerText = `${String(stopMins).padStart(2, '0')}:${String(stopSecs).padStart(2, '0')}`;
            }
            
            // 2. Format absolute cut time (HH:MM:SS)
            const absoluteSecs = Math.floor(startSec + currentTime);
            const absHrs = Math.floor(absoluteSecs / 3600);
            const absMins = Math.floor((absoluteSecs % 3600) / 60);
            const absSecs = absoluteSecs % 60;
            
            let absoluteText = '';
            if (absHrs > 0) {
                absoluteText = `${String(absHrs).padStart(2, '0')}:${String(absMins).padStart(2, '0')}:${String(absSecs).padStart(2, '0')}`;
            } else {
                absoluteText = `${String(absMins).padStart(2, '0')}:${String(absSecs).padStart(2, '0')}`;
            }
            if (absoluteSpan) {
                absoluteSpan.innerText = absoluteText;
            }
        });
    });
});

// Initialize bootstrap modal
let editClipModal = null;

function openEditClipModal(clipId, title, desc, subs) {
    if (!editClipModal) {
        editClipModal = new bootstrap.Modal(document.getElementById('modal_edit_clip'));
    }
    
    document.getElementById('edit_clip_id').value = clipId;
    document.getElementById('edit_clip_title').value = title;
    document.getElementById('edit_clip_desc').value = desc;
    
    const subsContainer = document.getElementById('subtitles_edit_list');
    subsContainer.innerHTML = '';
    
    if (subs && subs.length > 0) {
        subs.forEach((sub, idx) => {
            const minStr = Math.floor(sub.start_seconds / 60).toString().padStart(2, '0');
            const secStr = Math.floor(sub.start_seconds % 60).toString().padStart(2, '0');
            const timestamp = `[${minStr}:${secStr}]`;
            
            const textVal = sub.text_id || sub.text_en || '';
            
            const subRow = document.createElement('div');
            subRow.className = 'd-flex align-items-center gap-3 mb-3 pb-3 border-bottom border-gray-200';
            subRow.innerHTML = `
                <span class="fw-bold fs-8 min-w-70px" style="color: #6366f1;">${timestamp}</span>
                <input type="hidden" name="sub_start[]" value="${sub.start_seconds}">
                <input type="hidden" name="sub_end[]" value="${sub.end_seconds}">
                <input type="hidden" name="sub_en[]" value="${sub.text_en || ''}">
                <input type="text" name="sub_id[]" class="form-control form-control-sm form-control-solid rounded" value="${textVal.replace(/"/g, '&quot;')}" required>
            `;
            subsContainer.appendChild(subRow);
        });
    } else {
        subsContainer.innerHTML = '<span class="text-muted fs-8">Tidak ada data subtitle terstruktur untuk klip ini.</span>';
    }
    
    editClipModal.show();
}

function submitEditClipForm(event) {
    event.preventDefault();
    
    const clipId = document.getElementById('edit_clip_id').value;
    const title = document.getElementById('edit_clip_title').value;
    const desc = document.getElementById('edit_clip_desc').value;
    
    const btn = document.getElementById('btn_save_clip_changes');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Menyimpan...';
    btn.disabled = true;
    
    // Parse subtitles from list inputs
    const subRows = document.getElementById('subtitles_edit_list').children;
    const subtitles = [];
    
    for (let row of subRows) {
        const startInput = row.querySelector('input[name="sub_start[]"]');
        const endInput = row.querySelector('input[name="sub_end[]"]');
        const enInput = row.querySelector('input[name="sub_en[]"]');
        const idInput = row.querySelector('input[name="sub_id[]"]');
        
        if (startInput && endInput && idInput) {
            subtitles.push({
                start_seconds: parseFloat(startInput.value),
                end_seconds: parseFloat(endInput.value),
                text_en: idInput.value, // Set to edited value to prevent dual-sub split
                text_id: idInput.value
            });
        }
    }
    
    // Send AJAX request
    fetch(`/admin/game-clipper/clip/${clipId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('input[name="_token"]').value
        },
        body: JSON.stringify({
            title: title,
            description: desc,
            subtitles: subtitles
        })
    })
    .then(response => response.json())
    .then(data => {
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        if (data.success) {
            if (editClipModal) editClipModal.hide();
            
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: 'Sukses!',
                    text: 'Klip, Deskripsi, dan Subtitle Video berhasil diperbarui secara langsung!',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    window.location.reload();
                });
            } else {
                alert('Klip berhasil diperbarui!');
                window.location.reload();
            }
        } else {
            alert('Gagal memperbarui klip: ' + (data.message || 'Error tidak diketahui'));
        }
    })
    .catch(error => {
        btn.innerHTML = originalText;
        btn.disabled = false;
        alert('Terjadi kesalahan koneksi: ' + error.message);
    });
}

// Attach listener to edit buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-clip-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const clipId = this.getAttribute('data-clip-id');
            const title = this.getAttribute('data-clip-title');
            const desc = this.getAttribute('data-clip-desc');
            const subs = JSON.parse(this.getAttribute('data-clip-subs'));
            
            openEditClipModal(clipId, title, desc, subs);
        });
    });
});
</script>
@endsection

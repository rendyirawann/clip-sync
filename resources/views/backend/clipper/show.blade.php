@extends('backend.layout.app')
@section('title', 'Hasil AI Video Clipper')

@section('content')
<div class="mt-5 mb-10 container-fluid">
    <!-- Breadcrumbs & Navigation -->
    <div class="d-flex align-items-center justify-content-between mb-8 flex-wrap gap-4">
        <div>
            <ul class="breadcrumb breadcrumb-separatorless fw-semibold fs-7 my-1">
                <li class="breadcrumb-item text-muted">
                    <a href="{{ route('clipper.index') }}" class="text-muted text-hover-primary">Video Clipper</a>
                </li>
                <li class="breadcrumb-item">
                    <span class="bullet bg-gray-500 w-5px h-2px"></span>
                </li>
                <li class="breadcrumb-item text-gray-900">Detail Project</li>
            </ul>
            <h1 class="text-gray-900 fw-bold fs-1 mt-2">Detail Clipper: {{ $video->title }} 🎬</h1>
            @if(!empty($video->original_title) && $video->original_title !== $video->title)
                <span class="text-muted fs-6 fw-semibold d-block mt-1">
                    Original: <span class="fst-italic text-gray-700 fw-bold">{{ $video->original_title }}</span>
                </span>
            @endif
        </div>
        <div>
            <a href="{{ route('clipper.index') }}" class="btn btn-light-primary d-flex align-items-center">
                <i class="ki-duotone ki-left-square fs-3 me-2"><span class="path1"></span><span class="path2"></span></i>
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
                                <source src="{{ asset('storage/' . $video->file_path) }}" type="video/mp4">
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
                                <span class="badge badge-light-primary px-3 py-1 fs-8 me-2">Upload PC</span>
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

                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Selesai Diproses</span>
                        <span class="text-gray-800 fs-7 fw-bold d-block mt-1">{{ $video->updated_at->timezone('Asia/Jakarta')->format('d F Y - H:i T') }}</span>
                    </div>

                    <div class="mb-4">
                        <span class="text-muted fw-semibold d-block fs-8">Mesin Pemroses</span>
                        <span class="text-gray-800 fs-7 fw-bold d-block mt-1">
                            <span class="badge badge-light-success border border-success border-dashed px-3 py-1 fs-8 text-success me-2">
                                <i class="ki-duotone ki-electricity fs-6 text-success me-1"><span class="path1"></span><span class="path2"></span></i> Gemini 1.5 Flash
                            </span>
                            <span class="badge badge-light-info border border-info border-dashed px-3 py-1 fs-8 text-info">
                                <i class="ki-duotone ki-briefcase fs-6 text-info me-1"><span class="path1"></span><span class="path2"></span></i> FFmpeg
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
                        <span class="card-label fw-bold text-gray-900 fs-3 mb-1">Hasil Generasi Clip Highlights 🚀</span>
                        <span class="text-muted fw-semibold fs-7">Sistem berhasil memotong 3 klip video terbaik beserta dual subtitle ganda.</span>
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
                                        <div class="col-xl-6 bg-dark rounded-start overflow-hidden d-flex align-items-center justify-content-center" style="min-height: 250px;">
                                            <video id="player_{{ $clip->id }}" controls class="w-100 h-100" style="object-fit: contain;" crossorigin="anonymous">
                                                <source src="{{ asset('storage/' . $clip->file_path) }}" type="video/mp4">
                                                <!-- Dual Subtitles Track -->
                                                <track src="{{ asset('storage/clipper/' . $video->id . '/clip_' . $loop->iteration . '_sub.vtt') }}" kind="subtitles" srclang="id" label="Indo-En Dual Sub" default>
                                                Browser Anda tidak mendukung HTML5 video.
                                            </video>
                                        </div>

                                        <!-- Clip details Column -->
                                        <div class="col-xl-6 d-flex flex-column justify-content-between p-6">
                                            <div>
                                                <!-- Title & Badge -->
                                                <div class="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
                                                    <span class="badge badge-light-primary fw-bold px-3 py-1 fs-8">Klip #{{ $loop->iteration }}</span>
                                                    <span class="text-muted fs-8 fw-semibold">⏱️ {{ $clip->start_time }} - {{ $clip->end_time }}</span>
                                                </div>
                                                
                                                <!-- Caption Mockup Box (Draft Post) -->
                                                <div class="bg-light rounded p-4 mb-4 border border-gray-200 position-relative">
                                                    <span class="badge badge-light-dark fw-bold fs-9 px-2 py-1 position-absolute end-0 top-0 mt-3 me-3">Draft Post 📱</span>
                                                    
                                                    <span class="text-gray-600 fw-bold fs-9 d-block mb-1 text-uppercase tracking-wider">Judul Video:</span>
                                                    <h4 class="text-gray-900 fw-bold fs-6 mb-3 clip-title-text">{{ $clip->title }}</h4>
                                                    
                                                    <span class="text-gray-600 fw-bold fs-9 d-block mb-1 text-uppercase tracking-wider">Caption & Hashtags (FYP):</span>
                                                    <p class="text-gray-800 fs-7 mb-0 lh-base clip-desc-text" style="white-space: pre-line;">{{ $clip->description }}@if($video->source_type === 'youtube' && !empty($video->youtube_channel))


📌 Source: {{ $video->source_url }}
🎥 Channel: {{ $video->youtube_channel }}@endif</p>
                                                    
                                                    <div class="mt-4 pt-3 border-top border-gray-200 d-flex justify-content-end">
                                                        <button type="button" class="btn btn-light-primary btn-sm py-2 px-3 d-inline-flex align-items-center fw-bold fs-8" onclick="copyCaption(this)">
                                                            <i class="ki-duotone ki-copy fs-6 me-1.5"><span class="path1"></span><span class="path2"></span></i>
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
                                                                <div class="transcript-line py-1 border-bottom border-gray-100 cursor-pointer hover-text-primary fs-8 text-gray-700" 
                                                                     onclick="jumpToTime('player_{{ $clip->id }}', {{ $sub['start_seconds'] }})">
                                                                    <span class="text-primary fw-semibold me-2">[{{ sprintf('%02d:%02d', floor($sub['start_seconds'] / 60), $sub['start_seconds'] % 60) }}]</span>
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
                                                <a href="{{ asset('storage/' . $clip->file_path) }}" download class="btn btn-sm btn-success w-100 py-3 d-flex align-items-center justify-content-center fw-bold">
                                                    <i class="ki-duotone ki-cloud-download fs-5 me-2"><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span></i>
                                                    Download Klip (.MP4)
                                                </a>
                                                <a href="{{ asset('storage/clipper/' . $video->id . '/clip_' . $loop->iteration . '_sub.srt') }}" download class="btn btn-sm btn-light-info py-3 px-4" data-bs-toggle="tooltip" title="Download Subtitle SRT">
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
    background-color: rgba(62, 151, 255, 0.05);
    padding-left: 4px;
}
.truncate-3-lines {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;  
    overflow: hidden;
    text-overflow: ellipsis;
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
        button.classList.remove('btn-light-primary');
        button.classList.add('btn-success');
        
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
            button.classList.remove('btn-success');
            button.classList.add('btn-light-primary');
        }, 2500);
    }).catch(err => {
        console.error('Gagal menyalin text: ', err);
    });
}
</script>
@endsection

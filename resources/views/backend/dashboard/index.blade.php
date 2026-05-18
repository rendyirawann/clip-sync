@extends('backend.layout.app')
@section('title', 'Dashboard')
@section('content')

<div class="mt-5 mb-10">
    <!--begin::Hero Banner-->
    <div class="card border-0 mb-10 overflow-hidden" style="background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);">
        <div class="card-body p-10 p-lg-15 d-flex flex-column flex-md-row justify-content-between align-items-center position-relative">
            <!-- Background glow effects -->
            <div class="position-absolute translate-middle top-0 start-0 w-250px h-250px rounded-circle bg-primary opacity-25 blur-50"></div>
            <div class="position-absolute translate-middle bottom-0 end-0 w-250px h-250px rounded-circle bg-danger opacity-20 blur-50"></div>

            <div class="mb-8 mb-md-0 position-relative z-index-1">
                <h1 class="text-white fw-bolder fs-2x mb-3">Selamat Datang di Clip-Sync Admin!</h1>
                <p class="text-gray-400 fs-5 fw-semibold mb-6 max-w-600px">
                    Buat video klip pendek yang viral dari video YouTube atau file PC Anda secara instan menggunakan kecerdasan buatan (AI) lokal bertenaga GPU Anda!
                </p>
                <div class="d-flex align-items-center gap-3">
                    <a href="{{ url('/admin/clipper') }}" class="btn btn-primary fw-bold px-6 py-3">
                        <i class="ki-duotone ki-video-play fs-2 me-2">
                            <span class="path1"></span>
                            <span class="path2"></span>
                        </i>
                        Mulai Kliping Video
                    </a>
                    <a href="https://github.com/rendyirawann/clip-sync" target="_blank" class="btn btn-outline btn-outline-dashed btn-outline-default text-white fw-bold px-6 py-3">
                        <i class="ki-duotone ki-github fs-2 me-2">
                            <span class="path1"></span>
                            <span class="path2"></span>
                        </i>
                        Buka Repositori Git
                    </a>
                </div>
            </div>
            
            <div class="position-relative z-index-1">
                <!-- Premium SVG Illustration / Icon representing Video Slicing/AI -->
                <div class="bg-white bg-opacity-5 p-5 rounded-4 border border-white border-opacity-10 shadow-lg">
                    <i class="ki-duotone ki-colors-menu text-warning" style="font-size: 6rem;">
                        <span class="path1"></span>
                        <span class="path2"></span>
                        <span class="path3"></span>
                        <span class="path4"></span>
                    </i>
                </div>
            </div>
        </div>
    </div>
    <!--end::Hero Banner-->

    <!--begin::Stats Row-->
    <div class="row g-5 g-xl-10 mb-10">
        <!-- Card 1: Total Videos -->
        <div class="col-md-3">
            <div class="card card-flush h-md-100">
                <div class="card-header pt-5">
                    <div class="card-title d-flex flex-column">
                        <span class="fs-2hx fw-bold text-gray-900 me-2 lh-1 ls-n2">{{ $totalVideos }}</span>
                        <span class="text-gray-500 pt-1 fw-semibold fs-6">Total Video Terunggah</span>
                    </div>
                </div>
                <div class="card-body d-flex flex-column justify-content-end pe-0 pb-5">
                    <div class="d-flex align-items-center mb-2">
                        <div class="symbol symbol-35px me-3 bg-light-primary">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-video text-primary fs-2">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                </i>
                            </span>
                        </div>
                        <div class="fw-bold text-gray-800 fs-7">Antrean video clipper</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Card 2: Clips Generated -->
        <div class="col-md-3">
            <div class="card card-flush h-md-100">
                <div class="card-header pt-5">
                    <div class="card-title d-flex flex-column">
                        <span class="fs-2hx fw-bold text-gray-900 me-2 lh-1 ls-n2">{{ $totalClips }}</span>
                        <span class="text-gray-500 pt-1 fw-semibold fs-6">Klip AI Tergenerasi</span>
                    </div>
                </div>
                <div class="card-body d-flex flex-column justify-content-end pe-0 pb-5">
                    <div class="d-flex align-items-center mb-2">
                        <div class="symbol symbol-35px me-3 bg-light-success">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-check-circle text-success fs-2">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                </i>
                            </span>
                        </div>
                        <div class="fw-bold text-gray-800 fs-7">Momen viral terpotong</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Card 3: Active Tasks -->
        <div class="col-md-3">
            <div class="card card-flush h-md-100">
                <div class="card-header pt-5">
                    <div class="card-title d-flex flex-column">
                        <span class="fs-2hx fw-bold text-gray-900 me-2 lh-1 ls-n2 d-flex align-items-center gap-3">
                            {{ $processingVideos }}
                            @if($processingVideos > 0)
                                <span class="spinner-border spinner-border-sm text-primary" role="status"></span>
                            @endif
                        </span>
                        <span class="text-gray-500 pt-1 fw-semibold fs-6">Sedang Diproses</span>
                    </div>
                </div>
                <div class="card-body d-flex flex-column justify-content-end pe-0 pb-5">
                    <div class="d-flex align-items-center mb-2">
                        <div class="symbol symbol-35px me-3 bg-light-warning">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-loading text-warning fs-2">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                </i>
                            </span>
                        </div>
                        <div class="fw-bold text-gray-800 fs-7">
                            @if($processingVideos > 0)
                                Sedang bekerja di antrean...
                            @else
                                Tidak ada tugas aktif
                            @endif
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Card 4: Failed Tasks -->
        <div class="col-md-3">
            <div class="card card-flush h-md-100">
                <div class="card-header pt-5">
                    <div class="card-title d-flex flex-column">
                        <span class="fs-2hx fw-bold text-gray-900 me-2 lh-1 ls-n2">{{ $failedVideos }}</span>
                        <span class="text-gray-500 pt-1 fw-semibold fs-6">Tugas Gagal</span>
                    </div>
                </div>
                <div class="card-body d-flex flex-column justify-content-end pe-0 pb-5">
                    <div class="d-flex align-items-center mb-2">
                        <div class="symbol symbol-35px me-3 bg-light-danger">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-cross-circle text-danger fs-2">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                </i>
                            </span>
                        </div>
                        <div class="fw-bold text-gray-800 fs-7">Kendala sistem/durasi</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!--end::Stats Row-->

    <!--begin::Main Grid-->
    <div class="row g-5 g-xl-10">
        <!-- Col-8: Recent Videos Queue -->
        <div class="col-xl-8">
            <div class="card card-xl-stretch mb-5 mb-xl-10">
                <div class="card-header border-0 pt-5">
                    <h3 class="card-title align-items-start flex-column">
                        <span class="card-label fw-bold fs-3 text-gray-900">Aktivitas Kliping Terbaru</span>
                        <span class="text-muted mt-1 fw-semibold fs-7">5 video terakhir yang didaftarkan ke sistem antrean Anda</span>
                    </h3>
                    <div class="card-toolbar">
                        <a href="{{ url('/admin/clipper') }}" class="btn btn-sm btn-light btn-active-primary fw-bold">
                            Lihat Semua Antrean
                        </a>
                    </div>
                </div>
                <div class="card-body py-3">
                    <div class="table-responsive">
                        <table class="table table-row-dashed table-row-gray-300 align-middle gs-0 gy-4">
                            <thead>
                                <tr class="fw-bold text-muted border-0">
                                    <th class="p-0 min-w-200px">Detail Video</th>
                                    <th class="p-0 min-w-100px text-center">Sumber</th>
                                    <th class="p-0 min-w-120px text-center">Status</th>
                                    <th class="p-0 min-w-80px text-center">Jumlah Klip</th>
                                    <th class="p-0 min-w-100px text-end">Aksi</th>
                                </tr>
                            </thead>
                            <tbody>
                                @forelse($recentVideos as $video)
                                    <tr>
                                        <td>
                                            <div class="d-flex align-items-center">
                                                <div class="symbol symbol-45px me-5 bg-light-primary rounded">
                                                    <span class="symbol-label">
                                                        <i class="ki-duotone ki-film-svg text-primary fs-1">
                                                            <span class="path1"></span>
                                                            <span class="path2"></span>
                                                            <span class="path3"></span>
                                                            <span class="path4"></span>
                                                        </i>
                                                    </span>
                                                </div>
                                                <div class="d-flex flex-column">
                                                    <span class="text-gray-900 fw-bold text-hover-primary fs-6 text-truncate max-w-200px" title="{{ $video->title ?? 'Pemrosesan Video...' }}">
                                                        {{ $video->title ?? 'Video #' . substr($video->id, 0, 8) }}
                                                    </span>
                                                    <span class="text-muted fw-semibold fs-7 d-block">
                                                        {{ $video->created_at->diffForHumans() }}
                                                    </span>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="text-center">
                                            @if($video->source_type === 'youtube')
                                                <span class="badge badge-light-danger fw-bold fs-7">
                                                    <i class="ki-duotone ki-youtube text-danger fs-6 me-1">
                                                        <span class="path1"></span>
                                                        <span class="path2"></span>
                                                    </i>
                                                    YouTube
                                                </span>
                                            @else
                                                <span class="badge badge-light-primary fw-bold fs-7">
                                                    <i class="ki-duotone ki-file text-primary fs-6 me-1">
                                                        <span class="path1"></span>
                                                        <span class="path2"></span>
                                                    </i>
                                                    File PC
                                                </span>
                                            @endif
                                        </td>
                                        <td class="text-center">
                                            @if($video->status === 'completed')
                                                <span class="badge badge-light-success fw-bold fs-7">Selesai</span>
                                            @elseif($video->status === 'failed')
                                                <span class="badge badge-light-danger fw-bold fs-7" title="{{ $video->error_message }}">Gagal</span>
                                            @elseif($video->status === 'pending')
                                                <span class="badge badge-light-warning fw-bold fs-7">Mengantre</span>
                                            @else
                                                <span class="badge badge-light-primary fw-bold fs-7 d-flex align-items-center justify-content-center gap-1">
                                                    <span class="spinner-border spinner-border-sm text-primary" style="width: 10px; height: 10px;" role="status"></span>
                                                    {{ ucfirst($video->status) }}
                                                </span>
                                            @endif
                                        </td>
                                        <td class="text-center fw-bold text-gray-800">
                                            {{ $video->clips_count }} / 3
                                        </td>
                                        <td class="text-end">
                                            @if($video->status === 'completed')
                                                <a href="{{ url('/admin/clipper/' . $video->id) }}" class="btn btn-sm btn-icon btn-bg-light btn-active-color-primary" title="Lihat Hasil Klip AI">
                                                    <i class="ki-duotone ki-eye fs-2">
                                                        <span class="path1"></span>
                                                        <span class="path2"></span>
                                                        <span class="path3"></span>
                                                    </i>
                                                </a>
                                            @else
                                                <a href="{{ url('/admin/clipper') }}" class="btn btn-sm btn-icon btn-bg-light btn-active-color-primary" title="Pantau Proses">
                                                    <i class="ki-duotone ki-arrow-right fs-2">
                                                        <span class="path1"></span>
                                                        <span class="path2"></span>
                                                    </i>
                                                </a>
                                            @endif
                                        </td>
                                    </tr>
                                @empty
                                    <tr>
                                        <td colspan="5" class="text-center py-10 text-muted fs-6">
                                            Belum ada aktivitas kliping video. Silakan mulai dengan tombol di atas!
                                        </td>
                                    </tr>
                                @endforelse
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Col-4: System & AI Engine Status -->
        <div class="col-xl-4">
            <div class="card card-xl-stretch mb-xl-10">
                <div class="card-header border-0 pt-5">
                    <h3 class="card-title align-items-start flex-column">
                        <span class="card-label fw-bold text-gray-900 fs-3">Status Engine AI Lokal</span>
                        <span class="text-muted mt-1 fw-semibold fs-7">Konfigurasi AI dan perangkat keras aktif</span>
                    </h3>
                </div>
                <div class="card-body">
                    <!-- Status Item 1: LLM Engine -->
                    <div class="d-flex align-items-center mb-7">
                        <div class="symbol symbol-40px me-4 bg-light-success">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-status text-success fs-2x">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                    <span class="path3"></span>
                                    <span class="path4"></span>
                                </i>
                            </span>
                        </div>
                        <div class="d-flex flex-column flex-grow-1">
                            <span class="text-gray-900 fw-bold fs-6">Ollama LLM Engine</span>
                            <span class="text-muted fw-semibold fs-7">Meta Llama 3 (8B Active)</span>
                        </div>
                        <span class="badge badge-light-success fw-bold">Online</span>
                    </div>

                    <!-- Status Item 2: Speech-to-Text -->
                    <div class="d-flex align-items-center mb-7">
                        <div class="symbol symbol-40px me-4 bg-light-success">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-microphone text-success fs-2x">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                </i>
                            </span>
                        </div>
                        <div class="d-flex flex-column flex-grow-1">
                            <span class="text-gray-900 fw-bold fs-6">Whisper Engine</span>
                            <span class="text-muted fw-semibold fs-7">faster-whisper (Base Model)</span>
                        </div>
                        <span class="badge badge-light-success fw-bold">Online</span>
                    </div>

                    <!-- Status Item 3: Hardware Acceleration -->
                    <div class="d-flex align-items-center mb-7">
                        <div class="symbol symbol-40px me-4 bg-light-primary">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-cpu text-primary fs-2x">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                    <span class="path3"></span>
                                    <span class="path4"></span>
                                </i>
                            </span>
                        </div>
                        <div class="d-flex flex-column flex-grow-1">
                            <span class="text-gray-900 fw-bold fs-6">Akselerasi Perangkat Keras</span>
                            <span class="text-muted fw-semibold fs-7">Nvidia GPU CUDA (RTX 3050)</span>
                        </div>
                        <span class="badge badge-light-primary fw-bold">CUDA Active</span>
                    </div>

                    <!-- Status Item 4: Database -->
                    <div class="d-flex align-items-center mb-7">
                        <div class="symbol symbol-40px me-4 bg-light-success">
                            <span class="symbol-label">
                                <i class="ki-duotone ki-data text-success fs-2x">
                                    <span class="path1"></span>
                                    <span class="path2"></span>
                                </i>
                            </span>
                        </div>
                        <div class="d-flex flex-column flex-grow-1">
                            <span class="text-gray-900 fw-bold fs-6">Database</span>
                            <span class="text-muted fw-semibold fs-7">PostgreSQL (clip_sync)</span>
                        </div>
                        <span class="badge badge-light-success fw-bold">Connected</span>
                    </div>

                    <!-- Separator -->
                    <div class="separator my-5"></div>

                    <!-- Tips Section -->
                    <div class="bg-light-primary rounded p-4 mt-5">
                        <h4 class="text-primary fw-bold mb-2 fs-6">💡 Tips Penggunaan</h4>
                        <p class="text-gray-800 fs-7 mb-0 lh-base">
                            Transkripsi AI berjalan 100% lokal di GPU RTX 3050 Anda. Pastikan aplikasi <strong>Ollama</strong> tetap berjalan di latar belakang (cek ikon Llama di taskbar Windows Anda) agar proses penentuan highlight klip berjalan sukses!
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!--end::Main Grid-->
</div>

@endsection

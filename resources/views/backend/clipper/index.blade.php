@extends('backend.layout.app')
@section('title', 'AI Video Clipper Dashboard')

@section('content')
<div class="mt-5 mb-10 container-fluid">
    <!-- Header Title -->
    <div class="d-flex align-items-center justify-content-between mb-8 flex-wrap gap-4">
        <div>
            <h1 class="text-gray-900 fw-bold fs-1 mb-1">AI Video Clipper 🎬</h1>
            <p class="text-muted fs-6">Unggah video atau masukkan link YouTube untuk membuat 3 klip video terbaik beserta subtitle ganda secara otomatis menggunakan AI.</p>
        </div>
        <div>
            <span class="badge badge-light-primary border border-primary border-dashed px-4 py-3 fs-7 fw-semibold">
                <i class="ki-duotone ki-electricity fs-6 text-primary me-2">
                    <span class="path1"></span><span class="path2"></span>
                </i>Powered by Gemini AI Modality
            </span>
        </div>
    </div>

    <!-- Alert Success / Error -->
    @if(session('success'))
        <div class="alert alert-dismissible bg-light-success border border-success d-flex flex-column flex-sm-row p-5 mb-10 rounded">
            <i class="ki-duotone ki-check-circle fs-2hx text-success me-4 mb-5 mb-sm-0"><span class="path1"></span><span class="path2"></span></i>
            <div class="d-flex flex-column pe-0 pe-sm-10">
                <h4 class="fw-bold text-success">Berhasil!</h4>
                <span>{{ session('success') }}</span>
            </div>
            <button type="button" class="position-absolute position-sm-relative m-2 m-sm-0 top-0 end-0 btn btn-icon ms-sm-auto" data-bs-dismiss="alert">
                <i class="ki-duotone ki-cross fs-1 text-success"><span class="path1"></span><span class="path2"></span></i>
            </button>
        </div>
    @endif

    @if(session('error'))
        <div class="alert alert-dismissible bg-light-danger border border-danger d-flex flex-column flex-sm-row p-5 mb-10 rounded">
            <i class="ki-duotone ki-information-2 fs-2hx text-danger me-4 mb-5 mb-sm-0"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
            <div class="d-flex flex-column pe-0 pe-sm-10">
                <h4 class="fw-bold text-danger">Gagal!</h4>
                <span>{{ session('error') }}</span>
            </div>
            <button type="button" class="position-absolute position-sm-relative m-2 m-sm-0 top-0 end-0 btn btn-icon ms-sm-auto" data-bs-dismiss="alert">
                <i class="ki-duotone ki-cross fs-1 text-danger"><span class="path1"></span><span class="path2"></span></i>
            </button>
        </div>
    @endif

    <div class="row g-10">
        <!-- Input Form Section (Left) -->
        <div class="col-xl-5 col-lg-6">
            <div class="card shadow-sm border-0 h-100 bg-white">
                <div class="card-header border-0 pt-7">
                    <h3 class="card-title align-items-start flex-column">
                        <span class="card-label fw-bold text-gray-900 fs-3 mb-1">Buat Clipper Baru</span>
                        <span class="text-muted fw-semibold fs-7">Masukkan video Anda untuk di-generate menjadi 3 klip otomatis</span>
                    </h3>
                </div>

                <div class="card-body">
                    <form action="{{ route('clipper.store') }}" method="POST" enctype="multipart/form-data" id="clipperForm">
                        @csrf
                        
                        <!-- Video Title Optional -->
                        <div class="mb-8">
                            <label class="form-label fw-bold text-gray-800">Judul Project (Opsional)</label>
                            <input type="text" name="title" class="form-control form-control-solid" placeholder="Contoh: Highlight Podcast Deddy Corbuzier" value="{{ old('title') }}">
                            <div class="text-muted fs-8 mt-1">Mengosongkan kolom akan membuat judul default dengan tanggal saat ini.</div>
                        </div>

                        <!-- Source Type Toggle Tabs -->
                        <div class="mb-8">
                            <label class="form-label fw-bold text-gray-800 d-block mb-3">Pilih Sumber Video</label>
                            <div class="row g-4" data-kt-buttons="true" data-kt-buttons-target="[data-kt-button]">
                                <!-- YouTube Tab -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-danger d-flex align-items-center justify-content-center p-4 active" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="source_type" value="youtube" checked="checked" id="sourceTypeYoutube">
                                        <i class="ki-duotone ki-youtube fs-1 text-danger me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Link YouTube</span>
                                    </label>
                                </div>
                                <!-- Upload Tab -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-primary d-flex align-items-center justify-content-center p-4" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="source_type" value="upload" id="sourceTypeUpload">
                                        <i class="ki-duotone ki-file-up fs-1 text-primary me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Upload dari PC</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- Input Container (YouTube Input) -->
                        <div id="youtubeInputSection" class="mb-8">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-gray-800">URL / Link YouTube</label>
                                <div class="input-group input-group-solid">
                                    <span class="input-group-text"><i class="ki-duotone ki-youtube fs-3 text-danger"><span class="path1"></span><span class="path2"></span></i></span>
                                    <input type="url" name="youtube_url" class="form-control" placeholder="https://www.youtube.com/watch?v=..." value="{{ old('youtube_url') }}">
                                </div>
                                @error('youtube_url')
                                    <span class="text-danger fs-7 mt-1 d-block">{{ $message }}</span>
                                @enderror
                            </div>
                            <div class="bg-light-light rounded p-4 border border-dashed border-gray-300">
                                <div class="d-flex align-items-center">
                                    <i class="ki-duotone ki-information-3 fs-1 text-info me-3"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                    <span class="fs-7 text-gray-700">Video YouTube akan di-download secara otomatis di server background. Durasi video disarankan di bawah 15 menit agar pemrosesan cepat.</span>
                                </div>
                            </div>
                        </div>

                        <!-- Input Container (Upload File PC) -->
                        <div id="uploadInputSection" class="mb-8 d-none">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-gray-800">File Video (PC)</label>
                                
                                <div class="file-upload-wrapper border border-dashed border-primary rounded p-8 text-center bg-light-primary hover-elevate-up transition-all position-relative" style="cursor: pointer;">
                                    <input type="file" name="video_file" id="videoFileInput" class="position-absolute top-0 start-0 w-100 h-100 opacity-0" style="cursor: pointer;" accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska">
                                    <i class="ki-duotone ki-cloud-change fs-3x text-primary mb-3"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                    <h5 class="fw-bold text-gray-800" id="uploadFileText">Seret file ke sini atau klik untuk memilih</h5>
                                    <p class="text-muted fs-8 mb-0">Format: MP4, MOV, AVI, MKV. Ukuran Maksimal: 100MB.</p>
                                </div>
                                @error('video_file')
                                    <span class="text-danger fs-7 mt-1 d-block">{{ $message }}</span>
                                @enderror
                            </div>
                        </div>

                        <!-- AI Engine Selector -->
                        <div class="mb-8 border border-dashed border-gray-300 rounded p-6 bg-white">
                            <label class="form-label fw-bold text-gray-800 d-block mb-3">Mesin AI Pemroses (AI Engine)</label>
                            <div class="row g-4 mb-4" data-kt-buttons="true" data-kt-buttons-target="[data-kt-button]">
                                <!-- Gemini Tab -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-success d-flex align-items-center justify-content-center p-4 active" data-kt-button="true" id="labelEngineGemini">
                                        <input class="btn-check" type="radio" name="provider" value="gemini" checked="checked" id="engineGemini">
                                        <i class="ki-duotone ki-electricity fs-1 text-success me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Gemini (Cloud)</span>
                                    </label>
                                </div>
                                <!-- Ollama Tab -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-warning d-flex align-items-center justify-content-center p-4" data-kt-button="true" id="labelEngineLocal">
                                        <input class="btn-check" type="radio" name="provider" value="local" id="engineLocal">
                                        <i class="ki-duotone ki-home-trend-up fs-1 text-warning me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Ollama (Local)</span>
                                    </label>
                                </div>
                            </div>

                            <!-- Ollama Model Selector (Hidden by default unless 'local' is chosen) -->
                            <div id="ollamaModelSection" class="d-none bg-light-warning rounded p-5 border border-dashed border-warning mt-4">
                                <div class="mb-4">
                                    <label class="form-label fw-bold text-warning">Model Ollama yang Digunakan</label>
                                    <select name="model" id="ollamaModelSelect" class="form-select form-select-solid">
                                        <option value="llama3" selected>llama3 (Default)</option>
                                        <option value="qwen">qwen</option>
                                        <option value="mistral">mistral</option>
                                        <option value="custom">Tulis Model Sendiri (Custom)...</option>
                                    </select>
                                </div>
                                <div id="customModelSection" class="d-none mb-2">
                                    <label class="form-label fw-bold text-gray-800">Nama Model Custom</label>
                                    <input type="text" name="custom_model" class="form-control form-control-solid" placeholder="Contoh: qwen2.5:7b atau gemma:7b">
                                    <div class="text-muted fs-9 mt-1">Pastikan Anda sudah mengunduh model ini di laptop Anda dengan perintah `ollama run <nama-model>`</div>
                                </div>
                                <div class="d-flex align-items-center mt-2">
                                    <i class="ki-duotone ki-information-2 fs-4 text-warning me-2"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                    <span class="fs-8 text-gray-700">Pastikan aplikasi Ollama di laptop Anda sudah aktif dan model sudah di-download.</span>
                                </div>
                            </div>
                        </div>

                        <!-- Video Orientation Selector -->
                        <div class="mb-8 border border-dashed border-gray-300 rounded p-6 bg-white">
                            <label class="form-label fw-bold text-gray-800 d-block mb-3">Orientasi Video Hasil Klip (Aspect Ratio)</label>
                            <div class="row g-4" data-kt-buttons="true" data-kt-buttons-target="[data-kt-button]">
                                <!-- Landscape 16:9 Card -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-primary d-flex flex-column align-items-center justify-content-center p-5 active" data-kt-button="true" id="labelOrientationLandscape">
                                        <input class="btn-check" type="radio" name="orientation" value="16:9" checked="checked" id="orientationLandscape">
                                        <!-- Visual landscape rectangle -->
                                        <div class="border border-2 border-primary rounded mb-3 bg-light-primary d-flex align-items-center justify-content-center" style="width: 70px; height: 40px; transition: all 0.3s ease;">
                                            <i class="ki-duotone ki-screen fs-1 text-primary"><span class="path1"></span><span class="path2"></span></i>
                                        </div>
                                        <span class="fw-bold fs-7">Landscape (16:9)</span>
                                        <span class="text-muted fs-9 mt-1">Format YouTube/Layar Lebar</span>
                                    </label>
                                </div>
                                <!-- Vertical 9:16 Card -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-success d-flex flex-column align-items-center justify-content-center p-5" data-kt-button="true" id="labelOrientationVertical">
                                        <input class="btn-check" type="radio" name="orientation" value="9:16" id="orientationVertical">
                                        <!-- Visual vertical rectangle -->
                                        <div class="border border-2 border-success rounded mb-3 bg-light-success d-flex align-items-center justify-content-center" style="width: 40px; height: 70px; transition: all 0.3s ease;">
                                            <i class="ki-duotone ki-phone fs-1 text-success"><span class="path1"></span><span class="path2"></span></i>
                                        </div>
                                        <span class="fw-bold fs-7">Vertical (9:16)</span>
                                        <span class="text-muted fs-9 mt-1">Format TikTok/Shorts/Reels</span>
                                    </label>
                                </div>
                            </div>
                            <div class="text-muted fs-9 mt-3">
                                <i class="ki-duotone ki-information-2 fs-5 text-gray-500 me-1"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                Format Vertical (9:16) akan secara otomatis memotong bagian tengah (center crop) video agar pas di layar handphone.
                            </div>
                        </div>

                        <!-- Advanced Settings Accordion -->
                        <div class="card border border-dashed border-gray-300 mb-8 bg-light-light rounded">
                            <div class="card-header border-0 min-h-auto py-4 px-6 cursor-pointer" data-bs-toggle="collapse" data-bs-target="#advancedSettingsCollapse">
                                <h4 class="card-title fw-bold text-gray-800 fs-6 mb-0 d-flex align-items-center">
                                    <i class="ki-duotone ki-setting-4 fs-4 text-primary me-2"><span class="path1"></span><span class="path2"></span></i>
                                    Pengaturan Klip & Watermark (Opsional)
                                </h4>
                                <div class="card-toolbar">
                                    <i class="ki-duotone ki-down fs-5 text-gray-500 transition-all collapse-icon"></i>
                                </div>
                            </div>
                            <div id="advancedSettingsCollapse" class="collapse show px-6 pb-6">
                                <div class="row g-5">
                                    <!-- Clip Count -->
                                    <div class="col-12">
                                        <label class="form-label fw-semibold text-gray-700">Jumlah Klip yang Dihasilkan</label>
                                        <select name="clip_count" class="form-select form-select-solid">
                                            <option value="1">1 Video Klip</option>
                                            <option value="2">2 Video Klip</option>
                                            <option value="3" selected>3 Video Klip (Default)</option>
                                            <option value="4">4 Video Klip</option>
                                            <option value="5">5 Video Klip</option>
                                            <option value="6">6 Video Klip</option>
                                            <option value="8">8 Video Klip</option>
                                            <option value="10">10 Video Klip</option>
                                        </select>
                                    </div>
                                    <!-- Target Duration Selector Dropdown -->
                                    <div class="col-12">
                                        <label class="form-label fw-semibold text-gray-700">Target Durasi Klip Video</label>
                                        <select name="duration" class="form-select form-select-solid">
                                            <option value="30">30 Detik</option>
                                            <option value="60">60 Detik</option>
                                            <option value="90" selected>90 Detik (Default)</option>
                                            <option value="120">120 Detik (2 Menit)</option>
                                            <option value="180">180 Detik (3 Menit)</option>
                                            <option value="360">360 Detik (6 Menit)</option>
                                        </select>
                                        <div class="text-muted fs-8 mt-1">Sistem akan memotong klip dengan panjang sekitar durasi target yang Anda pilih.</div>
                                    </div>
                                    <!-- Watermark Text -->
                                    <div class="col-12">
                                        <label class="form-label fw-semibold text-gray-700">Teks Watermark (Transparan di Tengah)</label>
                                        <div class="input-group input-group-solid">
                                            <span class="input-group-text"><i class="ki-duotone ki-text fs-3 text-primary"><span class="path1"></span><span class="path2"></span></i></span>
                                            <input type="text" name="watermark" class="form-control" placeholder="Contoh: @rendyirawan" value="{{ old('watermark') }}">
                                        </div>
                                        <div class="text-muted fs-9 mt-1">Watermark akan dirender transparan di tengah-tengah video klip Anda secara elegan.</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Submit Button -->
                        <div class="pt-4">
                            <button type="submit" class="btn btn-primary w-100 py-4 fs-6 fw-bold shadow hover-scale transition-all" id="btnSubmit">
                                <span class="indicator-label d-flex align-items-center justify-content-center">
                                    <i class="ki-duotone ki-electricity fs-4 me-2"><span class="path1"></span><span class="path2"></span></i>
                                    Proses Video & Generate Clips
                                </span>
                                <span class="indicator-progress d-none">
                                    Tunggu sebentar... <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                                </span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Task List Section (Right) -->
        <div class="col-xl-7 col-lg-6">
            <div class="card shadow-sm border-0 h-100 bg-white">
                <div class="card-header border-0 pt-7">
                    <h3 class="card-title align-items-start flex-column">
                        <span class="card-label fw-bold text-gray-900 fs-3 mb-1">Riwayat & Status Video Clipper</span>
                        <span class="text-muted fw-semibold fs-7">Pantau jalannya proses generate video Anda di sini</span>
                    </h3>
                </div>

                <div class="card-body" id="statusTableContainer">
                    <!-- Check if videos exist -->
                    @if($videos->isEmpty())
                        <div class="text-center py-20">
                            <i class="ki-duotone ki-folder-question fs-5x text-gray-300 mb-5"><span class="path1"></span><span class="path2"></span></i>
                            <h4 class="fw-bold text-gray-700">Belum Ada Project Video</h4>
                            <p class="text-muted fs-7 max-w-400px mx-auto">Silakan masukkan link YouTube atau upload video dari laptop Anda di form sebelah kiri untuk memulai.</p>
                        </div>
                    @else
                        <div class="table-responsive">
                            <table class="table align-middle table-row-dashed fs-6 gy-5">
                                <thead>
                                    <tr class="text-start text-muted fw-bold fs-7 text-uppercase gs-0">
                                        <th class="min-w-150px">Project</th>
                                        <th class="min-w-100px">Sumber</th>
                                        <th class="min-w-120px text-center">Status</th>
                                        <th class="min-w-80px text-center">Klip</th>
                                        <th class="min-w-100px text-end">Aksi</th>
                                    </tr>
                                </thead>
                                <tbody class="text-gray-600 fw-semibold">
                                    @foreach($videos as $video)
                                        <tr>
                                            <!-- Project Title & Created Date -->
                                            <td>
                                                <div class="d-flex flex-column">
                                                    <div class="d-flex align-items-center flex-wrap gap-2 mb-1">
                                                        <span class="text-gray-900 fw-bold text-hover-primary fs-6 truncate-2-lines">{{ $video->title }}</span>
                                                        @if($video->provider === 'local')
                                                            <span class="badge badge-light-warning border border-warning border-dashed px-2 py-0.5 fs-9 text-warning" data-bs-toggle="tooltip" title="Offline AI Engine">
                                                                Local ({{ $video->model }})
                                                            </span>
                                                        @else
                                                            <span class="badge badge-light-success border border-success border-dashed px-2 py-0.5 fs-9 text-success" data-bs-toggle="tooltip" title="Cloud AI Engine">
                                                                Gemini
                                                            </span>
                                                        @endif

                                                        <!-- Aspect Ratio Orientation Badge -->
                                                        @if(($video->orientation ?? '16:9') === '9:16')
                                                            <span class="badge badge-light-primary border border-primary border-dashed px-2 py-0.5 fs-9 text-primary" data-bs-toggle="tooltip" title="Vertical Crop">
                                                                <i class="ki-duotone ki-phone fs-9 text-primary me-0.5"><span class="path1"></span><span class="path2"></span></i> 9:16
                                                            </span>
                                                        @else
                                                            <span class="badge badge-light-dark border border-gray-400 border-dashed px-2 py-0.5 fs-9 text-gray-700" data-bs-toggle="tooltip" title="Landscape Video">
                                                                <i class="ki-duotone ki-screen fs-9 text-gray-700 me-0.5"><span class="path1"></span><span class="path2"></span></i> 16:9
                                                            </span>
                                                        @endif
                                                    </div>
                                                    <span class="text-muted fs-8">{{ $video->created_at->timezone('Asia/Jakarta')->format('d M Y H:i T') }}</span>
                                                </div>
                                            </td>
                                            
                                            <!-- Source Type Label -->
                                            <td>
                                                @if($video->source_type === 'youtube')
                                                    <span class="badge badge-light-danger d-inline-flex align-items-center py-2 px-3 fs-8">
                                                        <i class="fab fa-youtube text-danger me-2 fs-6"></i> YouTube
                                                    </span>
                                                @else
                                                    <span class="badge badge-light-primary d-inline-flex align-items-center py-2 px-3 fs-8">
                                                        <i class="ki-duotone ki-laptop fs-6 text-primary me-2"><span class="path1"></span><span class="path2"></span></i> Upload PC
                                                    </span>
                                                @endif
                                            </td>

                                            <!-- Status Processing Badges -->
                                            <td class="text-center">
                                                @if($video->status === 'pending')
                                                    <span class="badge badge-light-secondary border border-secondary border-dashed px-3 py-2 fs-8 text-gray-700">
                                                        <span class="bullet bullet-dot bg-secondary me-2"></span> Mengantre
                                                    </span>
                                                @elseif($video->status === 'downloading')
                                                    <span class="badge badge-light-info border border-info border-dashed px-3 py-2 fs-8 text-info">
                                                        <span class="spinner-border spinner-border-sm me-2 text-info" style="width: 10px; height: 10px;"></span> Men-download...
                                                    </span>
                                                @elseif($video->status === 'transcribing')
                                                    <span class="badge badge-light-warning border border-warning border-dashed px-3 py-2 fs-8 text-warning pulse">
                                                        <span class="bullet bullet-dot bg-warning me-2"></span> AI Transcribe...
                                                    </span>
                                                @elseif($video->status === 'clipping')
                                                    <span class="badge badge-light-primary border border-primary border-dashed px-3 py-2 fs-8 text-primary pulse">
                                                        <span class="bullet bullet-dot bg-primary me-2"></span> AI Slicing...
                                                    </span>
                                                @elseif($video->status === 'completed')
                                                    <span class="badge badge-light-success border border-success border-dashed px-3 py-2 fs-8 text-success">
                                                        <i class="ki-duotone ki-check fs-6 text-success me-1"></i> Selesai
                                                    </span>
                                                @elseif($video->status === 'failed')
                                                    <span class="badge badge-light-danger border border-danger border-dashed px-3 py-2 fs-8 text-danger cursor-pointer" data-bs-toggle="tooltip" data-bs-placement="top" title="{{ $video->error_message }}">
                                                        <i class="ki-duotone ki-cross fs-6 text-danger me-1"></i> Gagal ⚠️
                                                    </span>
                                                @endif
                                            </td>

                                            <!-- Generated Clip Counts -->
                                            <td class="text-center">
                                                @if($video->status === 'completed')
                                                    <span class="badge badge-success px-3 py-2 fs-7 fw-bold shadow-sm rounded-circle">{{ $video->clips_count }}</span>
                                                @else
                                                    <span class="text-muted fs-7">-</span>
                                                @endif
                                            </td>

                                            <!-- Action Buttons -->
                                            <td class="text-end">
                                                <div class="d-flex align-items-center justify-content-end gap-2">
                                                    @if($video->status === 'completed')
                                                        <a href="{{ route('clipper.show', $video->id) }}" class="btn btn-sm btn-icon btn-bg-light btn-active-color-success" data-bs-toggle="tooltip" title="Lihat Hasil Klip">
                                                            <i class="ki-duotone ki-eye fs-2"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                                        </a>
                                                    @endif

                                                    <form action="{{ route('clipper.destroy', $video->id) }}" method="POST" onsubmit="return confirm('Apakah Anda yakin ingin menghapus project ini beserta seluruh video klip di dalamnya?')">
                                                        @csrf
                                                        @method('DELETE')
                                                        <button type="submit" class="btn btn-sm btn-icon btn-bg-light btn-active-color-danger" data-bs-toggle="tooltip" title="Hapus Project">
                                                            <i class="ki-duotone ki-trash fs-2"><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span><span class="path5"></span></i>
                                                        </button>
                                                    </form>
                                                </div>
                                            </td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Pagination -->
                        <div class="d-flex justify-content-end mt-4">
                            {{ $videos->links() }}
                        </div>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>

<style>
/* CSS micro-animations & layout helpers */
.pulse {
    animation: shadow-pulse 1.5s infinite ease-in-out;
}
@keyframes shadow-pulse {
    0% {
        box-shadow: 0 0 0 0px rgba(241, 180, 23, 0.4);
    }
    100% {
        box-shadow: 0 0 0 8px rgba(241, 180, 23, 0);
    }
}
.truncate-2-lines {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;  
    overflow: hidden;
    text-overflow: ellipsis;
}
.hover-elevate-up {
    transition: all 0.25s ease-out;
}
.hover-elevate-up:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const radioYoutube = document.getElementById('sourceTypeYoutube');
    const radioUpload = document.getElementById('sourceTypeUpload');
    const youtubeSection = document.getElementById('youtubeInputSection');
    const uploadSection = document.getElementById('uploadInputSection');
    const videoFileInput = document.getElementById('videoFileInput');
    const uploadFileText = document.getElementById('uploadFileText');
    const form = document.getElementById('clipperForm');
    const btnSubmit = document.getElementById('btnSubmit');

    // Toggle Inputs between Youtube & Local Upload
    radioYoutube.addEventListener('change', function() {
        if(this.checked) {
            youtubeSection.classList.remove('d-none');
            uploadSection.classList.add('d-none');
        }
    });

    radioUpload.addEventListener('change', function() {
        if(this.checked) {
            uploadSection.classList.remove('d-none');
            youtubeSection.classList.add('d-none');
        }
    });

    // Toggle AI Engine Options (Gemini vs Ollama Local)
    const radioGemini = document.getElementById('engineGemini');
    const radioLocal = document.getElementById('engineLocal');
    const ollamaModelSection = document.getElementById('ollamaModelSection');
    const ollamaModelSelect = document.getElementById('ollamaModelSelect');
    const customModelSection = document.getElementById('customModelSection');

    radioGemini.addEventListener('change', function() {
        if(this.checked) {
            ollamaModelSection.classList.add('d-none');
        }
    });

    radioLocal.addEventListener('change', function() {
        if(this.checked) {
            ollamaModelSection.classList.remove('d-none');
        }
    });

    ollamaModelSelect.addEventListener('change', function() {
        if(this.value === 'custom') {
            customModelSection.classList.remove('d-none');
        } else {
            customModelSection.classList.add('d-none');
        }
    });

    // Update File input text on selection
    videoFileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            const fileName = this.files[0].name;
            const fileSize = (this.files[0].size / (1024 * 1024)).toFixed(2);
            uploadFileText.innerText = `${fileName} (${fileSize} MB)`;
            uploadFileText.parentElement.classList.remove('bg-light-primary', 'border-primary');
            uploadFileText.parentElement.classList.add('bg-light-success', 'border-success');
        }
    });

    // Form submission indicator
    form.addEventListener('submit', function() {
        btnSubmit.setAttribute('disabled', 'true');
        btnSubmit.querySelector('.indicator-label').classList.add('d-none');
        btnSubmit.querySelector('.indicator-progress').classList.remove('d-none');
    });

    // Real-time Status Polling (AJAX DOM Parsing)
    function pollStatus() {
        fetch(window.location.href)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newTableContainer = doc.getElementById('statusTableContainer');
                
                if (newTableContainer) {
                    document.getElementById('statusTableContainer').innerHTML = newTableContainer.innerHTML;
                    
                    // Re-initialize Bootstrap tooltips for new elements
                    if (typeof bootstrap !== 'undefined') {
                        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                            return new bootstrap.Tooltip(tooltipTriggerEl)
                        });
                    }
                }
            })
            .catch(error => console.error("Error polling status:", error));
    }

    // Run polling every 3.5 seconds
    setInterval(pollStatus, 3500);
});
</script>
@endsection

@extends('backend.layout.app')
@section('title', 'Game & Anime Video Clipper')

@section('content')
<div class="mt-5 mb-10 container-fluid">
    <!-- Header Title -->
    <div class="d-flex align-items-center justify-content-between mb-8 flex-wrap gap-4">
        <div>
            <h1 class="text-gray-900 fw-bold fs-1 mb-1">Game & Anime Clipper 🎮✨</h1>
            <p class="text-muted fs-6">Highlight momen-momen terbaik game atau potong adegan anime favorit Anda dengan tambahan musik latar Phonk estetik secara otomatis.</p>
        </div>
        <div>
            <span class="badge badge-light-indigo border border-indigo border-dashed px-4 py-3 fs-7 fw-semibold" style="color: #6366f1; border-color: #6366f1 !important;">
                <i class="ki-duotone ki-electricity fs-6 me-2" style="color: #6366f1;">
                    <span class="path1"></span><span class="path2"></span>
                </i>Gaming & Phonk Style Edition
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
                        <span class="card-label fw-bold text-gray-900 fs-3 mb-1">Buat Klip Highlights & Phonk</span>
                        <span class="text-muted fw-semibold fs-7">Masukkan video gameplay/anime dan padukan dengan BGM Phonk</span>
                    </h3>
                </div>

                <div class="card-body">
                    <form action="{{ route('game-clipper.store') }}" method="POST" enctype="multipart/form-data" id="clipperForm">
                        @csrf
                        
                        <!-- Video Title Optional -->
                        <div class="mb-8">
                            <label class="form-label fw-bold text-gray-800">Judul Project (Opsional)</label>
                            <input type="text" name="title" class="form-control form-control-solid" placeholder="Contoh: Valorant Clutch Highlights or Naruto Edit" value="{{ old('title') }}">
                            <div class="text-muted fs-8 mt-1">Mengosongkan kolom akan membuat judul default dengan tanggal saat ini.</div>
                        </div>

                        <!-- Source Type Toggle Tabs -->
                        <div class="mb-8">
                            <label class="form-label fw-bold text-gray-800 d-block mb-3">Pilih Sumber Video</label>
                            <div class="row g-4" data-kt-buttons="true" data-kt-buttons-target="[data-kt-button]">
                                <!-- YouTube Tab -->
                                <div class="col-md-4 col-12">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-danger d-flex align-items-center justify-content-center p-4 {{ old('source_type', 'youtube') === 'youtube' ? 'active' : '' }}" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="source_type" value="youtube" {{ old('source_type', 'youtube') === 'youtube' ? 'checked="checked"' : '' }} id="sourceTypeYoutube">
                                        <i class="ki-duotone ki-youtube fs-1 text-danger me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Link YouTube</span>
                                    </label>
                                </div>
                                <!-- Upload Tab -->
                                <div class="col-md-4 col-12">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-primary d-flex align-items-center justify-content-center p-4 {{ old('source_type') === 'upload' ? 'active' : '' }}" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="source_type" value="upload" {{ old('source_type') === 'upload' ? 'checked="checked"' : '' }} id="sourceTypeUpload">
                                        <i class="ki-duotone ki-file-up fs-1 text-primary me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Upload PC</span>
                                    </label>
                                </div>
                                <!-- Local Path Tab -->
                                <div class="col-md-4 col-12">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-warning d-flex align-items-center justify-content-center p-4 {{ old('source_type') === 'local_path' ? 'active' : '' }}" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="source_type" value="local_path" {{ old('source_type') === 'local_path' ? 'checked="checked"' : '' }} id="sourceTypeLocalPath">
                                        <i class="ki-duotone ki-folder fs-1 text-warning me-2"><span class="path1"></span><span class="path2"></span></i>
                                        <span class="fw-bold">Path Lokal</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- Input Container (YouTube Input) -->
                        <div id="youtubeInputSection" class="mb-8 {{ old('source_type', 'youtube') === 'youtube' ? '' : 'd-none' }}">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-gray-800">URL / Link YouTube Gameplay / Anime</label>
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
                                    <span class="fs-7 text-gray-700">Link YouTube gameplay/anime akan di-download secara otomatis. Disarankan durasi di bawah 10 menit.</span>
                                </div>
                            </div>
                        </div>

                        <!-- Input Container (Upload File PC) -->
                        <div id="uploadInputSection" class="mb-8 {{ old('source_type') === 'upload' ? '' : 'd-none' }}">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-gray-800">File Video Game / Anime (PC)</label>
                                
                                <div class="file-upload-wrapper border border-dashed border-primary rounded p-8 text-center bg-light-primary hover-elevate-up transition-all position-relative" style="cursor: pointer;">
                                    <input type="file" name="video_file" id="videoFileInput" class="position-absolute top-0 start-0 w-100 h-100 opacity-0" style="cursor: pointer;" accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska">
                                    <i class="ki-duotone ki-cloud-change fs-3x text-primary mb-3"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                    <h5 class="fw-bold text-gray-800" id="uploadFileText">Seret file gameplay ke sini atau klik untuk memilih</h5>
                                    <p class="text-muted fs-8 mb-0">Format: MP4, MOV, AVI, MKV. Ukuran Maksimal: 100MB.</p>
                                </div>
                                @error('video_file')
                                    <span class="text-danger fs-7 mt-1 d-block">{{ $message }}</span>
                                @enderror
                            </div>
                        </div>

                        <!-- Input Container (Local Absolute Path) -->
                        <div id="localPathInputSection" class="mb-8 {{ old('source_type') === 'local_path' ? '' : 'd-none' }}">
                            <div class="mb-4">
                                <label class="form-label fw-bold text-gray-800">Path File Video Game / Anime Lokal (Absolute Path)</label>
                                <div class="input-group input-group-solid">
                                    <span class="input-group-text"><i class="ki-duotone ki-folder fs-3 text-warning"><span class="path1"></span><span class="path2"></span></i></span>
                                    <input type="text" name="local_path" class="form-control" placeholder="Contoh: D:\Videos\my_large_video.mp4" value="{{ old('local_path') }}">
                                </div>
                                @error('local_path')
                                    <span class="text-danger fs-7 mt-1 d-block">{{ $message }}</span>
                                @enderror
                            </div>
                            <div class="bg-light-warning rounded p-4 border border-dashed border-warning">
                                <div class="d-flex align-items-center">
                                    <i class="ki-duotone ki-information-2 fs-1 text-warning me-3"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                    <span class="fs-7 text-gray-800">Bebas upload file raksasa (5GB+)! Cukup copy-paste absolute path video dari disk lokal (localhost). Format didukung: MP4, MOV, AVI, MKV.</span>
                                </div>
                            </div>
                        </div>

                        <!-- ==================== NEW: Content Type Selection (Gameplay vs Anime) ==================== -->
                        <div class="mb-8 border border-dashed border-gray-300 rounded p-6 bg-white">
                            <label class="form-label fw-bold text-gray-800 d-block mb-3 fs-5">
                                <i class="ki-duotone ki-element-11 fs-3 me-2 text-primary"><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span></i>
                                Tipe Konten Video 🎨✨
                            </label>
                            <p class="text-muted fs-8 mb-4">Pilih jenis konten video Anda agar kecerdasan AI dan gaya editing disesuaikan secara otomatis.</p>
                            <div class="row g-4" data-kt-buttons="true" data-kt-buttons-target="[data-kt-button]">
                                <!-- Gameplay Highlights Card -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-primary d-flex flex-column align-items-center justify-content-center p-5 active" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="content_type" value="gameplay" checked="checked">
                                        <div class="border border-2 border-primary rounded mb-3 bg-light-primary d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; transition: all 0.3s ease;">
                                            <i class="ki-duotone ki-controller fs-1 text-primary"><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span></i>
                                        </div>
                                        <span class="fw-bold fs-7">Gameplay 🎮💥</span>
                                        <span class="text-muted fs-9 mt-1">Highlights, Clutch & Hype</span>
                                    </label>
                                </div>
                                <!-- Anime Scene Card -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-danger d-flex flex-column align-items-center justify-content-center p-5" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="content_type" value="anime">
                                        <div class="border border-2 border-danger rounded mb-3 bg-light-danger d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; transition: all 0.3s ease;">
                                            <i class="ki-duotone ki-ghost fs-1 text-danger"><span class="path1"></span><span class="path2"></span></i>
                                        </div>
                                        <span class="fw-bold fs-7">Anime Scene 🌸⚔️</span>
                                        <span class="text-muted fs-9 mt-1">Dialogue & Fight/Sad Scene</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- ==================== NEW: Phonk BGM Selection Card ==================== -->
                        <div class="mb-8 border border-dashed border-indigo rounded p-6 bg-light-primary bg-opacity-5" style="border-color: #6366f1 !important;">
                            <label class="form-label fw-bold d-block mb-3 fs-5" style="color: #4f46e5;">
                                <i class="ki-duotone ki-music fs-3 me-2" style="color: #6366f1;"><span class="path1"></span><span class="path2"></span></i>
                                Background Music (BGM Phonk) 🎧🔥
                            </label>
                            <p class="text-muted fs-8 mb-4">Pilih bagaimana BGM Phonk dicampur ke dalam video gameplay. Suara asli video tetap dominan, Phonk menjadi latar estetik.</p>

                            <!-- BGM Type Selection -->
                            <div class="row g-3 mb-5">
                                <div class="col-4">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-dark d-flex flex-column align-items-center justify-content-center p-3 active text-center w-100 h-100" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="bgm_type" value="none" checked="checked" id="bgmTypeNone">
                                        <span class="fw-bold fs-7">Tanpa BGM</span>
                                    </label>
                                </div>
                                <div class="col-4">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-indigo d-flex flex-column align-items-center justify-content-center p-3 text-center w-100 h-100" data-kt-button="true" style="--indigo: #6366f1;">
                                        <input class="btn-check" type="radio" name="bgm_type" value="local" id="bgmTypeLocal">
                                        <span class="fw-bold fs-7">Folder Phonk</span>
                                    </label>
                                </div>
                                <div class="col-4">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-danger d-flex flex-column align-items-center justify-content-center p-3 text-center w-100 h-100" data-kt-button="true">
                                        <input class="btn-check" type="radio" name="bgm_type" value="youtube" id="bgmTypeYoutube">
                                        <span class="fw-bold fs-7">YouTube BGM</span>
                                    </label>
                                </div>
                            </div>

                            <!-- BGM Sub-Section: Local MP3 Dropdown -->
                            <div id="bgmLocalSection" class="d-none mb-4">
                                <label class="form-label fw-bold text-gray-800 fs-7">Pilih Lagu Phonk dari Folder</label>
                                <select name="bgm_local_track" class="form-select form-select-solid select-bgm">
                                    <option value="" disabled selected>-- Pilih Lagu Phonk --</option>
                                    @foreach($bgmTracks as $track)
                                        <option value="{{ $track }}">{{ ucwords(str_replace(['_', '.mp3'], [' ', ''], $track)) }}</option>
                                    @endforeach
                                </select>
                                <div class="text-muted fs-9 mt-1">Lagu ini diambil dinamis dari folder <code>storage/app/public/bgm/phonk</code>. Anda bisa meletakkan file MP3 baru di sana!</div>
                                @error('bgm_local_track')
                                    <span class="text-danger fs-7 mt-1 d-block">{{ $message }}</span>
                                @enderror
                            </div>

                            <!-- BGM Sub-Section: YouTube BGM Link -->
                            <div id="bgmYoutubeSection" class="d-none mb-4">
                                <label class="form-label fw-bold text-gray-800 fs-7">URL / Link YouTube untuk BGM</label>
                                <div class="input-group input-group-solid">
                                    <span class="input-group-text"><i class="ki-duotone ki-youtube fs-3 text-danger"><span class="path1"></span><span class="path2"></span></i></span>
                                    <input type="url" name="bgm_youtube_url" class="form-control" placeholder="Pasti link YouTube Phonk / musik yang diinginkan..." value="{{ old('bgm_youtube_url') }}">
                                </div>
                                <div class="text-muted fs-9 mt-1">Sistem background job akan men-download audio saja dan me-mix ke dalam klip video secara otomatis!</div>
                                @error('bgm_youtube_url')
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

                            <!-- Ollama Model Selector -->
                            <div id="ollamaModelSection" class="d-none bg-light-warning rounded p-5 border border-dashed border-warning mt-4">
                                <div class="mb-4">
                                    <label class="form-label fw-bold text-warning">Model Ollama yang Digunakan</label>
                                    <select name="model" id="ollamaModelSelect" class="form-select form-select-solid">
                                        <option value="llama3.1" selected>llama3.1 (Default)</option>
                                        <option value="qwen2.5">qwen2.5</option>
                                        <option value="mistral">mistral</option>
                                        <option value="custom">Tulis Model Sendiri (Custom)...</option>
                                    </select>
                                </div>
                                <div id="customModelSection" class="d-none mb-2">
                                    <label class="form-label fw-bold text-gray-800">Nama Model Custom</label>
                                    <input type="text" name="custom_model" class="form-control form-control-solid" placeholder="Contoh: qwen2.5:7b">
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
                                        <div class="border border-2 border-primary rounded mb-3 bg-light-primary d-flex align-items-center justify-content-center" style="width: 70px; height: 40px; transition: all 0.3s ease;">
                                            <i class="ki-duotone ki-screen fs-1 text-primary"><span class="path1"></span><span class="path2"></span></i>
                                        </div>
                                        <span class="fw-bold fs-7">Landscape (16:9)</span>
                                        <span class="text-muted fs-9 mt-1">Format Layar Lebar Gameplay</span>
                                    </label>
                                </div>
                                <!-- Vertical 9:16 Card -->
                                <div class="col-6">
                                    <label class="btn btn-outline btn-outline-dashed btn-active-light-success d-flex flex-column align-items-center justify-content-center p-5" data-kt-button="true" id="labelOrientationVertical">
                                        <input class="btn-check" type="radio" name="orientation" value="9:16" id="orientationVertical">
                                        <div class="border border-2 border-success rounded mb-3 bg-light-success d-flex align-items-center justify-content-center" style="width: 40px; height: 70px; transition: all 0.3s ease;">
                                            <i class="ki-duotone ki-phone fs-1 text-success"><span class="path1"></span><span class="path2"></span></i>
                                        </div>
                                        <span class="fw-bold fs-7">Vertical (9:16)</span>
                                        <span class="text-muted fs-9 mt-1">Format TikTok/Shorts/Reels Edit</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- Reframer Mode Selection -->
                        <div class="mb-8 border border-dashed border-gray-300 rounded p-6 bg-white">
                            <label class="form-label fw-bold text-gray-800 fs-6 mb-3">Mode Pemrosesan AI & Reframer 🚀</label>
                            <div class="row g-4">
                                <!-- Standard Option -->
                                <div class="col-12">
                                    <label class="d-flex flex-stack text-start btn btn-outline btn-outline-dashed btn-active-light-primary p-5 active w-100" style="cursor: pointer;">
                                        <div class="d-flex align-items-start">
                                            <div class="form-check form-check-custom form-check-solid form-check-sm me-4 mt-1">
                                                <input class="form-check-input" type="radio" name="engine_mode" value="standard" checked />
                                            </div>
                                            <div>
                                                <div class="fw-bold text-gray-800 fs-6">Standard (Fast)</div>
                                                <div class="text-muted fs-8 mt-1">Potong tengah (center crop) statis, sangat cepat dan ringan CPU.</div>
                                            </div>
                                        </div>
                                    </label>
                                </div>

                                <!-- Opsi A Option -->
                                <div class="col-12">
                                    <label class="d-flex flex-stack text-start btn btn-outline btn-outline-dashed btn-active-light-primary p-5 w-100" style="cursor: pointer;">
                                        <div class="d-flex align-items-start">
                                            <div class="form-check form-check-custom form-check-solid form-check-sm me-4 mt-1">
                                                <input class="form-check-input" type="radio" name="engine_mode" value="opsi_a" />
                                            </div>
                                            <div>
                                                <div class="fw-bold text-gray-800 fs-6">Opsi A (YOLO + FaceMesh)</div>
                                                <div class="text-muted fs-8 mt-1">Cinematic camera pans, Rule of Thirds, lip-sync volume & karaoke subtitle.</div>
                                            </div>
                                        </div>
                                    </label>
                                </div>

                                <!-- Opsi B Option -->
                                <div class="col-12">
                                    <label class="d-flex flex-stack text-start btn btn-outline btn-outline-dashed btn-active-light-primary p-5 w-100" style="cursor: pointer;">
                                        <div class="d-flex align-items-start">
                                            <div class="form-check form-check-custom form-check-solid form-check-sm me-4 mt-1">
                                                <input class="form-check-input" type="radio" name="engine_mode" value="opsi_b" />
                                            </div>
                                            <div>
                                                <div class="fw-bold text-gray-800 fs-6">Opsi B (Smart Hybrid)</div>
                                                <div class="text-muted fs-8 mt-1">Kualitas sama persis Opsi A + optimasi pelacakan cepat & hemat CPU 10x!</div>
                                            </div>
                                        </div>
                                    </label>
                                </div>
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
                                        </select>
                                    </div>
                                    <!-- Watermark Text -->
                                    <div class="col-12">
                                        <label class="form-label fw-semibold text-gray-700">Teks Watermark (Transparan di Tengah)</label>
                                        <div class="input-group input-group-solid">
                                            <span class="input-group-text"><i class="ki-duotone ki-text fs-3 text-primary"><span class="path1"></span><span class="path2"></span></i></span>
                                            <input type="text" name="watermark" class="form-control" placeholder="Contoh: @rendyirawan" value="{{ old('watermark') }}">
                                        </div>
                                    </div>
                                    <!-- Burn Subtitles Checkbox Toggle -->
                                    <div class="col-12">
                                        <div class="d-flex flex-stack border border-dashed border-gray-300 rounded p-4 bg-white">
                                            <div class="d-flex align-items-start">
                                                <div class="symbol symbol-30px me-3 mt-1">
                                                    <div class="symbol-label bg-light-warning">
                                                        <i class="ki-duotone ki-note-2 fs-5 text-warning"><span class="path1"></span><span class="path2"></span><span class="path3"></span><span class="path4"></span></i>
                                                    </div>
                                                </div>
                                                <div>
                                                    <label class="form-label fw-bold text-gray-800 d-block mb-0 fs-7">Bakar Subtitle ke Video (Hardcode) 🔥</label>
                                                    <span class="text-muted fs-8">Aktifkan untuk menempelkan teks subtitle karaoke estetik langsung ke video klip.</span>
                                                </div>
                                            </div>
                                            <div class="form-check form-check-custom form-check-solid form-check-sm ms-4">
                                                <input class="form-check-input" type="checkbox" name="burn_subtitles" value="1" checked />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Submit Button -->
                        <div class="pt-4">
                            <button type="submit" class="btn btn-primary w-100 py-4 fs-6 fw-bold shadow hover-scale transition-all" id="btnSubmit" style="background-color: #6366f1 !important; border-color: #6366f1 !important;">
                                <span class="indicator-label d-flex align-items-center justify-content-center">
                                    <i class="ki-duotone ki-electricity fs-4 me-2"><span class="path1"></span><span class="path2"></span></i>
                                    Proses Video & Campur Phonk BGM
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
                        <span class="card-label fw-bold text-gray-900 fs-3 mb-1">Riwayat & Status Game Clipper</span>
                        <span class="text-muted fw-semibold fs-7">Pantau jalannya proses generate video game/anime Anda di sini</span>
                    </h3>
                </div>

                <div class="card-body" id="statusTableContainer">
                    @if($videos->isEmpty())
                        <div class="text-center py-20">
                            <i class="ki-duotone ki-folder-question fs-5x text-gray-300 mb-5"><span class="path1"></span><span class="path2"></span></i>
                            <h4 class="fw-bold text-gray-700">Belum Ada Project Video Game</h4>
                            <p class="text-muted fs-7 max-w-400px mx-auto">Silakan masukkan link YouTube gameplay atau upload video game di form sebelah kiri untuk memulai.</p>
                        </div>
                    @else
                        <div class="table-responsive">
                            <table class="table align-middle table-row-dashed fs-6 gy-5">
                                <thead>
                                    <tr class="text-start text-muted fw-bold fs-7 text-uppercase gs-0">
                                        <th class="min-w-150px">Project</th>
                                        <th class="min-w-100px">BGM Phonk</th>
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
                                                            <span class="badge badge-light-warning border border-warning border-dashed px-2 py-0.5 fs-9 text-warning">
                                                                Local
                                                            </span>
                                                        @else
                                                            <span class="badge badge-light-success border border-success border-dashed px-2 py-0.5 fs-9 text-success">
                                                                Gemini
                                                            </span>
                                                        @endif

                                                        @if($video->source_type === 'youtube')
                                                            <span class="badge badge-light-danger border border-danger border-dashed px-2 py-0.5 fs-9 text-danger">
                                                                YouTube
                                                            </span>
                                                        @elseif($video->source_type === 'local_path')
                                                            <span class="badge badge-light-warning border border-warning border-dashed px-2 py-0.5 fs-9 text-warning" data-bs-toggle="tooltip" title="{{ $video->file_path }}">
                                                                Path Lokal
                                                            </span>
                                                        @else
                                                            <span class="badge badge-light-primary border border-primary border-dashed px-2 py-0.5 fs-9 text-primary">
                                                                Upload PC
                                                            </span>
                                                        @endif

                                                        @if(($video->orientation ?? '16:9') === '9:16')
                                                            <span class="badge badge-light-primary border border-primary border-dashed px-2 py-0.5 fs-9 text-primary">
                                                                9:16
                                                            </span>
                                                        @else
                                                            <span class="badge badge-light-dark border border-gray-400 border-dashed px-2 py-0.5 fs-9 text-gray-700">
                                                                16:9
                                                            </span>
                                                        @endif
                                                    </div>
                                                    <span class="text-muted fs-8">{{ $video->created_at->timezone('Asia/Jakarta')->format('d M Y H:i T') }}</span>
                                                </div>
                                            </td>
                                            
                                            <!-- BGM Type Label -->
                                            <td>
                                                @if($video->bgm_type === 'none' || empty($video->bgm_track))
                                                    <span class="badge badge-light-secondary d-inline-flex align-items-center py-2 px-3 fs-8">
                                                        No Music
                                                    </span>
                                                @elseif($video->bgm_type === 'youtube')
                                                    <span class="badge badge-light-danger d-inline-flex align-items-center py-2 px-3 fs-8" data-bs-toggle="tooltip" title="{{ $video->bgm_track }}">
                                                        <i class="fab fa-youtube text-danger me-2 fs-6"></i> YT Phonk
                                                    </span>
                                                @else
                                                    <span class="badge badge-light-indigo d-inline-flex align-items-center py-2 px-3 fs-8" style="color: #6366f1; background-color: rgba(99, 102, 241, 0.1);" data-bs-toggle="tooltip" title="{{ $video->bgm_track }}">
                                                        <i class="ki-duotone ki-music text-primary me-2 fs-6"><span class="path1"></span><span class="path2"></span></i> {{ ucwords(str_replace(['_', '.mp3'], [' ', ''], $video->bgm_track)) }}
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
                                                        <a href="{{ route('game-clipper.show', $video->id) }}" class="btn btn-sm btn-icon btn-bg-light btn-active-color-success" data-bs-toggle="tooltip" title="Lihat Hasil Klip">
                                                            <i class="ki-duotone ki-eye fs-2"><span class="path1"></span><span class="path2"></span><span class="path3"></span></i>
                                                        </a>
                                                    @endif

                                                    <form action="{{ route('game-clipper.destroy', $video->id) }}" method="POST">
                                                        @csrf
                                                        @method('DELETE')
                                                        <button type="button" onclick="confirmDeleteProject(event, this)" class="btn btn-sm btn-icon btn-bg-light btn-active-color-danger" data-bs-toggle="tooltip" title="Hapus Project">
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
    const radioLocalPath = document.getElementById('sourceTypeLocalPath');
    const youtubeSection = document.getElementById('youtubeInputSection');
    const uploadSection = document.getElementById('uploadInputSection');
    const localPathSection = document.getElementById('localPathInputSection');
    const videoFileInput = document.getElementById('videoFileInput');
    const uploadFileText = document.getElementById('uploadFileText');
    const form = document.getElementById('clipperForm');
    const btnSubmit = document.getElementById('btnSubmit');

    // Toggle Inputs between Youtube, Local Upload, & Local Path
    function toggleSourceSections() {
        if (radioYoutube.checked) {
            youtubeSection.classList.remove('d-none');
            uploadSection.classList.add('d-none');
            if (localPathSection) localPathSection.classList.add('d-none');
        } else if (radioUpload.checked) {
            uploadSection.classList.remove('d-none');
            youtubeSection.classList.add('d-none');
            if (localPathSection) localPathSection.classList.add('d-none');
        } else if (radioLocalPath && radioLocalPath.checked) {
            if (localPathSection) localPathSection.classList.remove('d-none');
            youtubeSection.classList.add('d-none');
            uploadSection.classList.add('d-none');
        }
    }

    radioYoutube.addEventListener('change', toggleSourceSections);
    radioUpload.addEventListener('change', toggleSourceSections);
    if (radioLocalPath) {
        radioLocalPath.addEventListener('change', toggleSourceSections);
    }

    // Run once on load to ensure correct visibility based on old() validation state
    toggleSourceSections();

    // Toggle BGM selections
    const bgmTypeNone = document.getElementById('bgmTypeNone');
    const bgmTypeLocal = document.getElementById('bgmTypeLocal');
    const bgmTypeYoutube = document.getElementById('bgmTypeYoutube');
    const bgmLocalSection = document.getElementById('bgmLocalSection');
    const bgmYoutubeSection = document.getElementById('bgmYoutubeSection');

    function toggleBgmSections() {
        if (bgmTypeNone.checked) {
            bgmLocalSection.classList.add('d-none');
            bgmYoutubeSection.classList.add('d-none');
        } else if (bgmTypeLocal.checked) {
            bgmLocalSection.classList.remove('d-none');
            bgmYoutubeSection.classList.add('d-none');
        } else if (bgmTypeYoutube.checked) {
            bgmLocalSection.classList.add('d-none');
            bgmYoutubeSection.classList.remove('d-none');
        }
    }

    [bgmTypeNone, bgmTypeLocal, bgmTypeYoutube].forEach(radio => {
        if (radio) {
            radio.addEventListener('change', toggleBgmSections);
        }
    });

    // Run once at start
    toggleBgmSections();

    // Toggle AI Engine Options
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

    // Dynamic buttons highlight handler
    const buttons = document.querySelectorAll('[data-kt-button="true"]');
    buttons.forEach(button => {
        const input = button.querySelector('input[type="radio"]');
        if (input) {
            input.addEventListener('change', function() {
                const name = this.getAttribute('name');
                const siblings = document.querySelectorAll(`input[name="${name}"]`);
                siblings.forEach(sib => {
                    sib.parentElement.classList.remove('active');
                });
                if (this.checked) {
                    this.parentElement.classList.add('active');
                }
            });
        }
    });

    // Toggle active class on engine mode radio cards selection
    const engineRadios = document.querySelectorAll('input[name="engine_mode"]');
    engineRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            engineRadios.forEach(r => {
                const label = r.closest('label');
                if (label) {
                    label.classList.remove('active');
                }
            });
            if (this.checked) {
                const activeLabel = this.closest('label');
                if (activeLabel) {
                    activeLabel.classList.add('active');
                }
            }
        });
    });

    // Form submit loading visual response
    form.addEventListener('submit', function() {
        btnSubmit.setAttribute('data-kt-indicator', 'on');
        btnSubmit.querySelector('.indicator-label').classList.add('d-none');
        btnSubmit.querySelector('.indicator-progress').classList.remove('d-none');
        btnSubmit.disabled = true;
    });
});

function confirmDeleteProject(event, element) {
    event.preventDefault();
    Swal.fire({
        title: 'Apakah Anda yakin?',
        text: "Project ini dan semua klip video/subtitle di dalamnya akan dihapus permanen dari server!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Hapus!',
        cancelButtonText: 'Batal'
    }).then((result) => {
        if (result.isConfirmed) {
            element.closest('form').submit();
        }
    });
}
</script>
@endsection

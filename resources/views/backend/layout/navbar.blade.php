					<!--begin::Header-->
					<div id="kt_header" class="header" data-kt-sticky="true" data-kt-sticky-name="header" data-kt-sticky-animation="false" data-kt-sticky-offset="{default: '200px', lg: '300px'}">
						<!--begin::Container-->
						<div class="container-xxl d-flex align-items-center flex-lg-stack">
							<!--begin::Brand-->
							<div class="d-flex align-items-center flex-grow-1 flex-lg-grow-0 me-2 me-lg-5">
								<!--begin::Wrapper-->
								<div class="flex-grow-1">
									<!--begin::Aside toggle-->
									<button class="btn btn-icon btn-color-gray-800 btn-active-color-primary ms-n4 me-lg-12" id="kt_aside_toggle">
										<i class="ki-duotone ki-abstract-14 fs-1">
											<span class="path1"></span>
											<span class="path2"></span>
										</i>
									</button>
									<!--end::Aside toggle-->
									<!--begin::Header Logo-->
									<a href="index.html">
										<img alt="Logo" src="{{ asset('assets/media/logos/default-small.svg') }}" class="h-30px" />
									</a>
									<!--end::Header Logo-->
								</div>
								<!--end::Wrapper-->
</div>
							<!--end::Brand-->
							<!--begin::Toolbar wrapper-->
							<div class="d-flex align-items-stretch flex-shrink-0">
								<!--begin::Clip-Sync Notifications-->
								<div class="d-flex align-items-center ms-1 ms-lg-3 me-2">
									<!--begin::offcanvas toggle-->
									<button class="position-relative btn btn-color-gray-800 btn-icon btn-active-light-primary w-30px h-30px w-md-40px h-md-40px border-0 bg-transparent" data-bs-toggle="offcanvas" data-bs-target="#kt_offcanvas_notifications" aria-controls="kt_offcanvas_notifications">
										<i class="ki-duotone ki-notification-status fs-1">
											<span class="path1"></span>
											<span class="path2"></span>
											<span class="path3"></span>
											<span class="path4"></span>
										</i>
										<span class="bullet bullet-dot bg-danger h-6px w-6px position-absolute translate-middle top-0 start-50 animation-blink"></span>
									</button>
									<!--end::offcanvas toggle-->
								</div>
								<!--end::Clip-Sync Notifications-->
<!--begin::Theme mode-->
								<div class="d-flex align-items-center ms-1 ms-lg-3">
									<!--begin::Menu toggle-->
									<a href="#" class="btn btn-color-gray-800 btn-icon btn-active-light-primary w-30px h-30px w-md-40px h-md-40px" data-kt-menu-trigger="{default:'click', lg: 'hover'}" data-kt-menu-attach="parent" data-kt-menu-placement="bottom-end">
										<i class="ki-duotone ki-night-day theme-light-show fs-1">
											<span class="path1"></span>
											<span class="path2"></span>
											<span class="path3"></span>
											<span class="path4"></span>
											<span class="path5"></span>
											<span class="path6"></span>
											<span class="path7"></span>
											<span class="path8"></span>
											<span class="path9"></span>
											<span class="path10"></span>
										</i>
										<i class="ki-duotone ki-moon theme-dark-show fs-1">
											<span class="path1"></span>
											<span class="path2"></span>
										</i>
									</a>
									<!--begin::Menu toggle-->
									<!--begin::Menu-->
									<div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-title-gray-700 menu-icon-gray-500 menu-active-bg menu-state-color fw-semibold py-4 fs-base w-150px" data-kt-menu="true" data-kt-element="theme-mode-menu">
										<!--begin::Menu item-->
										<div class="menu-item px-3 my-0">
											<a href="#" class="menu-link px-3 py-2" data-kt-element="mode" data-kt-value="light">
												<span class="menu-icon" data-kt-element="icon">
													<i class="ki-duotone ki-night-day fs-2">
														<span class="path1"></span>
														<span class="path2"></span>
														<span class="path3"></span>
														<span class="path4"></span>
														<span class="path5"></span>
														<span class="path6"></span>
														<span class="path7"></span>
														<span class="path8"></span>
														<span class="path9"></span>
														<span class="path10"></span>
													</i>
												</span>
												<span class="menu-title">Light</span>
											</a>
										</div>
										<!--end::Menu item-->
										<!--begin::Menu item-->
										<div class="menu-item px-3 my-0">
											<a href="#" class="menu-link px-3 py-2" data-kt-element="mode" data-kt-value="dark">
												<span class="menu-icon" data-kt-element="icon">
													<i class="ki-duotone ki-moon fs-2">
														<span class="path1"></span>
														<span class="path2"></span>
													</i>
												</span>
												<span class="menu-title">Dark</span>
											</a>
										</div>
										<!--end::Menu item-->
										<!--begin::Menu item-->
										<div class="menu-item px-3 my-0">
											<a href="#" class="menu-link px-3 py-2" data-kt-element="mode" data-kt-value="system">
												<span class="menu-icon" data-kt-element="icon">
													<i class="ki-duotone ki-screen fs-2">
														<span class="path1"></span>
														<span class="path2"></span>
														<span class="path3"></span>
														<span class="path4"></span>
													</i>
												</span>
												<span class="menu-title">System</span>
											</a>
										</div>
										<!--end::Menu item-->
									</div>
									<!--end::Menu-->
								</div>
								<!--end::Theme mode-->
								<!--begin::User menu-->
								<div class="d-flex align-items-center ms-1 ms-lg-3">
									<!--begin::Menu wrapper-->
									<div class="btn btn-color-gray-800 btn-icon btn-active-light-primary w-30px h-30px w-md-40px h-md-40px position-relative btn btn-color-gray-800 btn-icon btn-active-light-primary w-30px h-30px w-md-40px h-md-40px" data-kt-menu-trigger="click" data-kt-menu-attach="parent" data-kt-menu-placement="bottom-end">
										<i class="ki-duotone ki-user fs-1">
											<span class="path1"></span>
											<span class="path2"></span>
										</i>
									</div>
									<!--begin::User account menu-->
									<div class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-800 menu-state-bg menu-state-color fw-semibold py-4 fs-6 w-275px" data-kt-menu="true">
										<!--begin::Menu item-->
										<div class="menu-item px-3">
											<div class="menu-content d-flex align-items-center px-3">
												<!--begin::Avatar-->
												<div class="symbol symbol-50px me-5">
													<img alt="Logo" src="{{ asset('assets/media/avatars/300-1.jpg') }}" />
												</div>
												<!--end::Avatar-->
												<!--begin::Username-->
												<div class="d-flex flex-column">
													<div class="fw-bold d-flex align-items-center fs-5">{{ auth()->user()->name ?? 'Administrator' }} 
													<span class="badge badge-light-success fw-bold fs-8 px-2 py-1 ms-2">{{ auth()->user()?->getRoleNames()->first() ?? 'Admin' }}</span></div>
													<a href="#" class="fw-semibold text-muted text-hover-primary fs-7">{{ auth()->user()->email ?? '' }}</a>
												</div>
												<!--end::Username-->
											</div>
										</div>
										<!--end::Menu item-->
										<!--begin::Menu separator-->
										<div class="separator my-2"></div>
										<!--end::Menu separator-->
										<!--begin::Menu item-->
										<div class="menu-item px-5">
											<a href="{{ route('account.index') }}" class="menu-link px-5">
												<i class="ki-duotone ki-profile-circle fs-5 me-2 text-gray-500">
													<span class="path1"></span>
													<span class="path2"></span>
													<span class="path3"></span>
												</i>
												My Profile
											</a>
										</div>
										<!--end::Menu item-->
										<!--begin::Menu separator-->
										<div class="separator my-2"></div>
										<!--end::Menu separator-->
										<!--begin::Menu item-->
										<div class="menu-item px-5">
											<a href="{{ route('logout') }}" onclick="event.preventDefault(); confirmSignOut();" class="menu-link px-5 text-danger">
												<i class="ki-duotone ki-entrance-left fs-5 me-2 text-danger">
													<span class="path1"></span>
													<span class="path2"></span>
												</i>
												Sign Out
											</a>
											<form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
												@csrf
											</form>
										</div>
										<!--end::Menu item-->
									</div>
									<!--end::User account menu-->
									<!--end::Menu wrapper-->
								</div>
								<!--end::User menu-->
</div>
							<!--end::Toolbar wrapper-->
						</div>
						<!--end::Container-->
					</div>
					<!--end::Header-->


<!-- Notification Offcanvas (Right Modal) -->
<div class="offcanvas offcanvas-end" tabindex="-1" id="kt_offcanvas_notifications" aria-labelledby="kt_offcanvas_notifications_label" style="width: 380px;">
    <div class="offcanvas-header bg-light py-5">
        <h5 class="offcanvas-title fw-bold text-gray-900" id="kt_offcanvas_notifications_label">
            <i class="ki-duotone ki-notification-status text-primary fs-2 me-2">
                <span class="path1"></span>
                <span class="path2"></span>
                <span class="path3"></span>
                <span class="path4"></span>
            </i>
            Notifikasi Clip-Sync
        </h5>
        <button type="button" class="btn btn-sm btn-icon btn-active-color-primary" data-bs-dismiss="offcanvas" aria-label="Close">
            <i class="ki-duotone ki-cross fs-2">
                <span class="path1"></span>
                <span class="path2"></span>
            </i>
        </button>
    </div>
    <div class="offcanvas-body p-6">
        <!-- Latest Activity Timeline or Notification Items -->
        <div class="timeline timeline-border-dashed">
            <!-- Item 1 -->
            <div class="timeline-item mb-6">
                <div class="timeline-line"></div>
                <div class="timeline-icon bg-light-success">
                    <i class="ki-duotone ki-check-circle text-success fs-2">
                        <span class="path1"></span>
                        <span class="path2"></span>
                    </i>
                </div>
                <div class="timeline-content">
                    <span class="fs-7 fw-semibold text-muted">Baru saja</span>
                    <div class="d-flex align-items-center mt-1">
                        <a href="/admin/clipper" class="fs-6 text-gray-800 text-hover-primary fw-bold">Video Clip Selesai!</a>
                        <span class="badge badge-light-success fs-9 px-2 py-0.5 ms-2">Sukses</span>
                    </div>
                    <p class="text-muted fs-7 mt-1 mb-0">Video clipper berhasil mengklip 3 highlight momen dengan subtitle bahasa Indonesia.</p>
                </div>
            </div>
            <!-- Item 2 -->
            <div class="timeline-item mb-6">
                <div class="timeline-line"></div>
                <div class="timeline-icon bg-light-warning">
                    <i class="ki-duotone ki-loading text-warning fs-2">
                        <span class="path1"></span>
                        <span class="path2"></span>
                    </i>
                </div>
                <div class="timeline-content">
                    <span class="fs-7 fw-semibold text-muted">5 menit yang lalu</span>
                    <div class="d-flex align-items-center mt-1">
                        <a href="/admin/clipper" class="fs-6 text-gray-800 text-hover-primary fw-bold">Sedang Mengklip Video</a>
                        <span class="badge badge-light-warning fs-9 px-2 py-0.5 ms-2">Proses</span>
                    </div>
                    <p class="text-muted fs-7 mt-1 mb-0">Model Whisper sedang melakukan transkripsi speech-to-text pada audio video.</p>
                </div>
            </div>
            <!-- Item 3 -->
            <div class="timeline-item mb-6">
                <div class="timeline-line"></div>
                <div class="timeline-icon bg-light-primary">
                    <i class="ki-duotone ki-cloud-download text-primary fs-2">
                        <span class="path1"></span>
                        <span class="path2"></span>
                    </i>
                </div>
                <div class="timeline-content">
                    <span class="fs-7 fw-semibold text-muted">15 menit yang lalu</span>
                    <div class="d-flex align-items-center mt-1">
                        <a href="/admin/clipper" class="fs-6 text-gray-800 text-hover-primary fw-bold">YouTube Berhasil Diunduh</a>
                        <span class="badge badge-light-primary fs-9 px-2 py-0.5 ms-2">Sukses</span>
                    </div>
                    <p class="text-muted fs-7 mt-1 mb-0">Video YouTube berhasil diunduh menggunakan engine yt-dlp secara lokal.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function confirmSignOut() {
    Swal.fire({
        title: 'Apakah Anda yakin?',
        text: "Anda akan keluar dari sesi admin Clip-Sync.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#f1416c',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, Keluar!',
        cancelButtonText: 'Batal',
        customClass: {
            confirmButton: 'btn btn-danger',
            cancelButton: 'btn btn-active-light'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('logout-form').submit();
        }
    });
}
</script>

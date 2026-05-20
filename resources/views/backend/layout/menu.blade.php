					<!--begin::Aside menu-->
					<div class="aside-menu flex-column-fluid">
						<!--begin::Aside Menu-->
						<div class="hover-scroll-overlay-y my-5 mx-2" id="kt_aside_menu_wrapper" data-kt-scroll="true" data-kt-scroll-activate="true" data-kt-scroll-height="auto" data-kt-scroll-dependencies="#kt_aside_footer" data-kt-scroll-wrappers="#kt_aside, #kt_aside_menu" data-kt-scroll-offset="2px">
							<!--begin::Menu-->
							<div class="menu menu-column menu-sub-indention menu-active-bg menu-state-primary menu-title-gray-700 fs-6 menu-rounded w-100 fw-semibold" id="#kt_aside_menu" data-kt-menu="true">
								
								<!--begin:Menu item-->
								<div class="menu-item pt-5">
									<!--begin:Menu content-->
									<div class="menu-content">
										<span class="menu-heading fw-bold text-uppercase fs-7">Main</span>
									</div>
									<!--end:Menu content-->
								</div>
								<!--end:Menu item-->

								<!--begin:Menu item-->
								<div class="menu-item">
									<!--begin:Menu link-->
									<a class="menu-link {{ request()->routeIs('dashboard') ? 'active' : '' }}" href="{{ route('dashboard') }}">
										<span class="menu-icon">
											<i class="ki-duotone ki-element-11 fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
												<span class="path3"></span>
												<span class="path4"></span>
											</i>
										</span>
										<span class="menu-title">Dashboard</span>
									</a>
									<!--end:Menu link-->
								</div>
								<!--end:Menu item-->

								<!--begin:Menu item-->
								<div class="menu-item">
									<!--begin:Menu link-->
									<a class="menu-link {{ request()->routeIs('clipper.*') ? 'active' : '' }}" href="{{ route('clipper.index') }}">
										<span class="menu-icon">
											<i class="ki-duotone ki-video fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
											</i>
										</span>
										<span class="menu-title">Video Clipper</span>
									</a>
									<!--end:Menu link-->
								</div>
								<!--end:Menu item-->

								<!--begin:Menu item-->
								<div class="menu-item">
									<!--begin:Menu link-->
									<a class="menu-link {{ request()->routeIs('game-clipper.*') ? 'active' : '' }}" href="{{ route('game-clipper.index') }}">
										<span class="menu-icon">
											<i class="ki-duotone ki-gamepad fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
											</i>
										</span>
										<span class="menu-title">Game & Anime Clipper</span>
									</a>
									<!--end:Menu link-->
								</div>
								<!--end:Menu item-->


								<!--begin:Menu item-->
								<div class="menu-item pt-5">
									<!--begin:Menu content-->
									<div class="menu-content">
										<span class="menu-heading fw-bold text-uppercase fs-7">Account</span>
									</div>
									<!--end:Menu content-->
								</div>
								<!--end:Menu item-->

								<!--begin:Menu item-->
								<div class="menu-item">
									<!--begin:Menu link-->
									<a class="menu-link {{ request()->routeIs('account.index') ? 'active' : '' }}" href="{{ route('account.index') }}">
										<span class="menu-icon">
											<i class="ki-duotone ki-address-book fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
												<span class="path3"></span>
											</i>
										</span>
										<span class="menu-title">My Profile</span>
									</a>
									<!--end:Menu link-->
								</div>
								<!--end:Menu item-->

								@can('view_resources')
								<!--begin:Menu item-->
								<div class="menu-item pt-5">
									<!--begin:Menu content-->
									<div class="menu-content">
										<span class="menu-heading fw-bold text-uppercase fs-7">Administration</span>
									</div>
									<!--end:Menu content-->
								</div>
								<!--end:Menu item-->

								<!--begin:Menu item-->
								<div data-kt-menu-trigger="click" class="menu-item menu-accordion {{ request()->routeIs('users.*') || request()->routeIs('roles.*') ? 'here show' : '' }}">
									<!--begin:Menu link-->
									<span class="menu-link">
										<span class="menu-icon">
											<i class="ki-duotone ki-abstract-28 fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
											</i>
										</span>
										<span class="menu-title">User Management</span>
										<span class="menu-arrow"></span>
									</span>
									<!--end:Menu link-->
									<!--begin:Menu sub-->
									<div class="menu-sub menu-sub-accordion">
										<!--begin:Menu item-->
										<div class="menu-item">
											<!--begin:Menu link-->
											<a class="menu-link {{ request()->routeIs('users.*') ? 'active' : '' }}" href="{{ route('users.index') }}">
												<span class="menu-bullet">
													<span class="bullet bullet-dot"></span>
												</span>
												<span class="menu-title">Users List</span>
											</a>
											<!--end:Menu link-->
										</div>
										<!--end:Menu item-->
										<!--begin:Menu item-->
										<div class="menu-item">
											<!--begin:Menu link-->
											<a class="menu-link {{ request()->routeIs('roles.*') ? 'active' : '' }}" href="{{ route('roles.index') }}">
												<span class="menu-bullet">
													<span class="bullet bullet-dot"></span>
												</span>
												<span class="menu-title">Roles & Permissions</span>
											</a>
											<!--end:Menu link-->
										</div>
										<!--end:Menu item-->
									</div>
									<!--end:Menu sub-->
								</div>
								<!--end:Menu item-->
								@endcan

								<!--begin:Menu item-->
								<div class="menu-item pt-5">
									<!--begin:Menu content-->
									<div class="menu-content">
										<span class="menu-heading fw-bold text-uppercase fs-7">System</span>
									</div>
									<!--end:Menu content-->
								</div>
								<!--end:Menu item-->

								<!--begin:Menu item-->
								<div class="menu-item">
									<!--begin:Menu link-->
									<a class="menu-link {{ request()->routeIs('settings.index') ? 'active' : '' }}" href="{{ route('settings.index') }}">
										<span class="menu-icon">
											<i class="ki-duotone ki-setting-2 fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
											</i>
										</span>
										<span class="menu-title">Settings</span>
									</a>
									<!--end:Menu link-->
								</div>
								<!--end:Menu item-->

								@can('view_help')
								<!--begin:Menu item-->
								<div class="menu-item">
									<!--begin:Menu link-->
									<a class="menu-link {{ request()->routeIs('log-activity.index') ? 'active' : '' }}" href="{{ route('log-activity.index') }}">
										<span class="menu-icon">
											<i class="ki-duotone ki-message-text-2 fs-2">
												<span class="path1"></span>
												<span class="path2"></span>
												<span class="path3"></span>
											</i>
										</span>
										<span class="menu-title">Log Activity</span>
									</a>
									<!--end:Menu link-->
								</div>
								<!--end:Menu item-->
								@endcan

							</div>
							<!--end::Menu-->
						</div>
						<!--end::Aside Menu-->
					</div>
					<!--end::Aside menu-->

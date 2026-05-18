<?php

namespace App\Http\Controllers\Backend\Dashboard;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Video;
use App\Models\Clip;

class DashboardAdminController extends Controller
{
    public function index()
    {
        $userId = auth()->id();
        
        $totalVideos = Video::where('user_id', $userId)->count();
        $totalClips = Clip::whereHas('video', function($q) use ($userId) {
            $q->where('user_id', $userId);
        })->count();
        
        $processingVideos = Video::where('user_id', $userId)
            ->whereIn('status', ['pending', 'downloading', 'transcribing', 'slicing'])
            ->count();
            
        $completedVideos = Video::where('user_id', $userId)
            ->where('status', 'completed')
            ->count();
            
        $failedVideos = Video::where('user_id', $userId)
            ->where('status', 'failed')
            ->count();
            
        $recentVideos = Video::where('user_id', $userId)
            ->withCount('clips')
            ->orderBy('created_at', 'desc')
            ->take(5)
            ->get();

        return view('backend.dashboard.index', compact(
            'totalVideos',
            'totalClips',
            'processingVideos',
            'completedVideos',
            'failedVideos',
            'recentVideos'
        ));
    }
}
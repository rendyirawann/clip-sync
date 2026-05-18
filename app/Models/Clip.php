<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Clip extends Model
{
    use HasFactory;

    protected $fillable = [
        'video_id',
        'title',
        'description',
        'file_path',
        'start_time',
        'end_time',
        'start_seconds',
        'end_seconds',
        'subtitles_srt',
        'subtitles_vtt',
        'subtitles_dual',
    ];

    protected $casts = [
        'subtitles_dual' => 'array',
    ];

    /**
     * Get the source video that owns the clip.
     */
    public function video(): BelongsTo
    {
        return $this->belongsTo(Video::class);
    }
}

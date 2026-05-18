<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Video extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'title',
        'original_title',
        'source_type',
        'source_url',
        'youtube_channel',
        'file_path',
        'clip_count',
        'clip_duration_min',
        'clip_duration_max',
        'watermark',
        'provider',
        'model',
        'orientation',
        'status',
        'error_message',
    ];

    /**
     * Get the user that owns the video.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the clips generated from this video.
     */
    public function clips(): HasMany
    {
        return $this->hasMany(Clip::class);
    }
}

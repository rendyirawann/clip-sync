<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('clips', function (Blueprint $table) {
            $table->id();
            $table->foreignId('video_id')->constrained('videos')->onDelete('cascade');
            $table->string('title');
            $table->text('description')->nullable();
            $table->text('file_path'); // path to clip video
            $table->string('start_time'); // e.g. 00:01:15
            $table->string('end_time'); // e.g. 00:01:45
            $table->integer('start_seconds');
            $table->integer('end_seconds');
            $table->longText('subtitles_srt')->nullable(); // Dual subtitles in SRT
            $table->longText('subtitles_vtt')->nullable(); // Dual subtitles in VTT (for video player)
            $table->json('subtitles_dual')->nullable(); // structured subtitles array
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('clips');
    }
};

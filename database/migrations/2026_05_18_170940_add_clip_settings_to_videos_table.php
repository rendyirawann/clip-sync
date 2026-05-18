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
        Schema::table('videos', function (Blueprint $table) {
            $table->integer('clip_count')->default(3)->after('youtube_channel');
            $table->integer('clip_duration_min')->default(30)->after('clip_count');
            $table->integer('clip_duration_max')->default(90)->after('clip_duration_min');
            $table->string('watermark')->nullable()->after('clip_duration_max');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('videos', function (Blueprint $table) {
            $table->dropColumn(['clip_count', 'clip_duration_min', 'clip_duration_max', 'watermark']);
        });
    }
};

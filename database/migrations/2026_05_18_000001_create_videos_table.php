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
        Schema::create('videos', function (Blueprint $table) {
            $table->id();
            $table->foreignUuid('user_id')->nullable()->constrained('users')->onDelete('cascade');
            $table->string('title')->nullable();
            $table->string('source_type'); // 'upload' or 'youtube'
            $table->text('source_url')->nullable(); // youtube url
            $table->text('file_path')->nullable(); // path to local source video
            $table->string('status')->default('pending'); // pending, downloading, transcribing, clipping, completed, failed
            $table->text('error_message')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('videos');
    }
};

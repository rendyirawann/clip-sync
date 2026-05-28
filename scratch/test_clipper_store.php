<?php
require __DIR__ . '/../vendor/autoload.php';
$app = require_once __DIR__ . '/../bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

use App\Http\Controllers\Backend\VideoClipperController;
use Illuminate\Http\Request;
use App\Models\User;

echo "Logging in test user...\n";
$user = User::first();
if (!$user) {
    echo "No user found in the database. Cannot continue test.\n";
    exit(1);
}
auth()->login($user);

echo "Creating mock request...\n";
$request = Request::create('/admin/clipper', 'POST', [
    'source_type' => 'youtube',
    'title' => 'Tinker Test YouTube',
    'youtube_url' => 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'clip_count' => 3,
    'duration' => 90,
    'provider' => 'gemini',
    'orientation' => '16:9',
    'engine_mode' => 'standard',
    'burn_subtitles' => 1,
    'language' => 'id'
]);

echo "Invoking VideoClipperController@store...\n";
$start = microtime(true);

try {
    $controller = app(VideoClipperController::class);
    $response = $controller->store($request);

    $duration = microtime(true) - $start;
    echo "Completed successfully! Target Redirect: " . $response->headers->get('Location') . " (took " . round($duration, 4) . " seconds)\n";
} catch (\Exception $e) {
    echo "FAILED with error: " . $e->getMessage() . "\n";
}

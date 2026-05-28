<?php
require __DIR__ . '/../vendor/autoload.php';
$app = require_once __DIR__ . '/../bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

echo "Attempting to write to database...\n";
$start = microtime(true);

$user = \App\Models\User::first();
if (!$user) {
    echo "No user found in the database. Cannot continue test.\n";
    exit(1);
}

$v = new \App\Models\Video();
$v->user_id = $user->id;
$v->title = 'Tinker Test';
$v->source_type = 'youtube';
$v->source_url = 'https://youtube.com';
$v->save();

$duration = microtime(true) - $start;
echo "Successfully wrote to database! ID: " . $v->id . " (took " . round($duration, 4) . " seconds)\n";

// Cleanup the test record
$v->delete();
echo "Successfully deleted test record.\n";

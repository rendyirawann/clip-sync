<?php
require __DIR__ . '/../vendor/autoload.php';
$app = require_once __DIR__ . '/../bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

$failedJob = \DB::table('failed_jobs')->latest('failed_at')->first();
if ($failedJob) {
    echo "Failed Job ID: " . $failedJob->id . "\n";
    echo "Connection: " . $failedJob->connection . "\n";
    echo "Queue: " . $failedJob->queue . "\n";
    echo "Failed At: " . $failedJob->failed_at . "\n";
    echo "Exception:\n" . substr($failedJob->exception, 0, 1000) . "...\n";
} else {
    echo "No failed jobs found in the failed_jobs table.\n";
}

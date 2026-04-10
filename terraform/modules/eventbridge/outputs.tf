output "schedule_arn" {
  value = aws_scheduler_schedule.btc_signal.arn
}

output "schedule_name" {
  value = aws_scheduler_schedule.btc_signal.name
}

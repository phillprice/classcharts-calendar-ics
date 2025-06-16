# ClassCharts Calendar Sync

![GitHub Actions Status](https://github.com/phillprice/classcharts-calendar-ics/workflows/Tests/badge.svg)

A serverless application that automatically syncs ClassCharts timetable data to iCalendar files, making school schedules easily accessible across all calendar applications. The system fetches data from ClassCharts and generates calendar files that are hosted on Amazon S3, allowing seamless subscription from Apple Calendar, Google Calendar, Outlook, and other calendar applications.

## Features

- **Automatic Syncing**: Updates calendars every 6 hours to keep timetables current
- **Multi-Student Support**: Manage calendars for multiple students from a single account
- **Secure Credential Storage**: Uses AWS Secrets Manager for secure credential management
- **Universal Calendar Access**: Compatible with any calendar app that supports iCal subscription
- **Local Testing**: Test functionality without AWS credentials using local mode
- **Easy Deployment**: Simple deployment with AWS SAM (Serverless Application Model)

## Quick Links

- [Getting Started](getting-started.md) - Quick setup guide
- [Configuration](configuration/index.md) - Configure environment variables and AWS resources
- [Deployment](deployment/index.md) - Deploy the application to AWS
- [Development](development/environment-setup.md) - Local development instructions
- [Calendar Usage](usage/calendar-access.md) - Access and use the generated calendars
- [Project Information](project/structure.md) - Project structure and contribution guidelines

## Architecture Overview

The ClassCharts Calendar Sync application uses AWS Lambda to periodically fetch data from the ClassCharts API and generate iCalendar files that are stored in Amazon S3. The generated calendar files are then available via public URLs that can be subscribed to from any calendar application.

```mermaid
graph LR
    A[AWS Lambda Function] -->|Run every 6 hours| B[ClassCharts API]
    B -->|Retrieve timetable data| A
    A -->|Generate iCalendar files| C[Amazon S3 Bucket]
    D[Calendar Apps] -->|Subscribe to| C
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/phillprice/classcharts-calendar-ics/blob/main/LICENSE) file for details.
# AWS S3 Sync Tool

A Python-based tool for efficiently downloading files from AWS S3 buckets with intelligent synchronization capabilities. This tool automatically skips files that are already up-to-date based on file size, modification time, and MD5 checksums.

## Features

- 🔍 **Smart Synchronization**: Only downloads files that have changed or don't exist locally
- 📊 **Multiple Comparison Methods**: Uses file size, modification time, and MD5 checksums for accurate change detection
- 📁 **Prefix Support**: Download files from specific S3 prefixes/folders
- 🚀 **Efficient**: Uses S3 pagination for handling large buckets
- 🛡️ **Error Handling**: Graceful error handling with informative messages
- 📝 **Progress Tracking**: Clear console output showing download progress and skipped files

## Prerequisites

- Python 3.6 or higher
- AWS credentials (Access Key and Secret Key)
- Required Python packages (see Installation section)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd aws-s3-sync
```

2. Install required dependencies:
```bash
pip install boto3
```

## Configuration

1. Edit the `config.json` file with your AWS credentials and settings:

```json
{
  "access_key": "YOUR_AWS_ACCESS_KEY",
  "secret_key": "YOUR_AWS_SECRET_KEY",
  "region": "ap-southeast-1",
  "bucket": "your-bucket-name",
  "prefix": "optional/prefix/path",
  "local_dir": "./downloaded"
}
```

### Configuration Options

- `access_key`: Your AWS Access Key ID
- `secret_key`: Your AWS Secret Access Key
- `region`: AWS region (default: ap-southeast-1)
- `bucket`: Name of your S3 bucket
- `prefix`: Optional S3 prefix/folder path to sync (leave empty for entire bucket)
- `local_dir`: Local directory where files will be downloaded (default: ./downloaded)

## Usage

Run the sync tool:

```bash
python s3_sync.py
```

The tool will:
1. Load configuration from `config.json`
2. Connect to your S3 bucket
3. List all objects under the specified prefix
4. Download only files that have changed or don't exist locally
5. Preserve S3 modification timestamps on local files

## How It Works

### Change Detection

The tool uses multiple methods to determine if a file needs to be downloaded:

1. **File Existence**: Files that don't exist locally are always downloaded
2. **Size Comparison**: Files with different sizes are considered changed
3. **Modification Time**: Files with different modification times are considered changed
4. **MD5 Checksum**: For files with simple ETags (no multipart), MD5 comparison is used

### Output Examples

```
🔍 Starting download from bucket: 'my-bucket', prefix: 'images'
📦 Found 5 objects in this page.
⬇️ Downloading: images/photo1.jpg -> ./downloaded/photo1.jpg
⏩ Skipping (same size & mtime): ./downloaded/photo2.jpg
✅ Already up to date: images/photo2.jpg
```

## Security Notes

- **Never commit your AWS credentials** to version control
- Consider using AWS IAM roles or environment variables for production use
- The `config.json` file is included in `.gitignore` to prevent accidental commits

## Error Handling

The tool handles various error scenarios:

- Missing or invalid AWS credentials
- Network connectivity issues
- S3 permission errors
- Invalid bucket names or prefixes
- Keyboard interrupts (Ctrl+C)

## Troubleshooting

### Common Issues

1. **"AWS credentials not found or invalid"**
   - Verify your access key and secret key in `config.json`
   - Ensure your AWS credentials have S3 read permissions

2. **"Failed to list bucket objects"**
   - Check if the bucket name is correct
   - Verify your AWS credentials have permission to list bucket contents

3. **"No files found under this prefix"**
   - Verify the prefix path exists in your S3 bucket
   - Check if the prefix ends with a forward slash if it's a folder

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE). 
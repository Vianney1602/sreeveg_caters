# AWS S3 Image Upload Setup Guide

## Overview
Your backend has been configured to upload images directly to AWS S3. This eliminates issues with local storage and ensures images are reliably accessible from your Neon database.

## Quick Setup Steps

### 1. Create AWS S3 Bucket
1. Go to [AWS S3 Console](https://console.aws.amazon.com/s3)
2. Click **Create bucket**
3. Enter a **Bucket name** (e.g., `cater-images-prod`)
4. Select your **AWS Region** (e.g., `us-east-1`)
5. **Uncheck** "Block all public access" (so images are publicly accessible)
6. Click **Create bucket**

### 2. Create IAM Access Keys
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam)
2. Click **Users** in the left menu
3. Create or select an existing user
4. Go to **Security credentials** tab
5. Click **Create access key**
6. Choose **Application running outside AWS**
7. Copy and save:
   - **Access Key ID**
   - **Secret Access Key**

### 3. Set Bucket Policy (Allow Public Read)
In S3 bucket settings, go to **Permissions** → **Bucket Policy** and add:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        },
        {
            "Sid": "AllowFullAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR-AWS-ACCOUNT-ID:user/YOUR-IAM-USER"
            },
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

Replace:
- `YOUR-BUCKET-NAME` with your bucket name
- `YOUR-AWS-ACCOUNT-ID` with your AWS account ID
- `YOUR-IAM-USER` with your IAM user name

### 4. Configure Environment Variables
Add these to your `.env` file (in the **backend** directory):

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_S3_BUCKET_NAME=your_bucket_name_here
AWS_S3_REGION=us-east-1
```

### 5. Install Dependencies
Run this in the **backend** directory:

```bash
pip install -r requirements.txt
```

Or install boto3 directly:

```bash
pip install boto3
```

## How It Works Now

### Upload Flow
1. Admin uploads image through dashboard
2. Frontend sends image to `/api/uploads/image`
3. Backend uploads image to S3
4. **S3 URL is returned and stored in Neon database** (e.g., `https://your-bucket.s3.us-east-1.amazonaws.com/images/uuid_filename.jpg`)
5. Image is immediately accessible and persists across restarts

### Image Display
- Images are stored as URLs in your Neon database (`MenuItem.image_url`)
- Frontend fetches the URL from the database
- Images load directly from S3 (no local server required)

### Image Deletion
- When an admin deletes or updates a menu item
- The old S3 image is automatically deleted from your bucket
- URL is removed from the database

## Troubleshooting

### "S3 upload failed" Error
**Check:**
- AWS credentials are correct in `.env`
- Bucket name is correct
- Region is correct
- IAM user has `s3:PutObject` permission
- Bucket policy allows public read access

### Images Not Showing
**Step 1:** Check browser console (F12) for image URL errors
**Step 2:** Verify the S3 URL in Neon database:
```sql
SELECT image_url FROM menu_items WHERE item_id = 1;
```

**Step 3:** Test the URL directly in browser - it should load the image

**Step 4:** If URL is missing from database, check admin dashboard upload response (Network tab)

### S3 Not Configured (Development)
If you don't have AWS configured, images will fall back to local storage:
- Saved to `backend/static/uploads/`
- URLs stored as `/api/uploads/image/{id}`
- Database stores full binary data
- ⚠️ Not recommended for production

## Testing the Integration

### Option 1: Via Admin Dashboard
1. Go to Admin Dashboard
2. Add a new menu item
3. Upload an image
4. Verify image appears in the menu
5. Check Network tab - should see S3 URL response

### Option 2: Direct API Test (cURL)
```bash
curl -X POST http://localhost:5000/api/uploads/image \
  -F "image=@/path/to/image.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response should include S3 URL:
```json
{
  "url": "https://your-bucket.s3.us-east-1.amazonaws.com/images/uuid_filename.jpg",
  "storage": "s3"
}
```

## FAQ

**Q: Will existing images still work?**
A: Yes! The code handles legacy image URLs (local files, API IDs). New uploads go to S3.

**Q: Do I need to migrate old images?**
A: Not required. Old images stay as-is. You can manually update them by re-uploading.

**Q: Is my bucket exposed to public?**
A: Only for reading images. Users cannot delete or modify objects. Admin controls are secured via IAM.

**Q: What's the cost?**
A: AWS S3 is ~$0.023 per GB/month for storage + data transfer costs. First 12 months include free tier (5GB).

**Q: Can I use other S3-compatible services?**
A: Yes! Min.io, DigitalOcean Spaces, etc. Update `AWS_S3_REGION` and the URL pattern in config if needed.

## Environment Variable Template

```env
# Database
DATABASE_URL=postgresql://user:pass@neon-host/dbname

# JWT
JWT_SECRET_KEY=your_jwt_secret_key

# Admin
ADMIN_USERNAME=hotelshanmugabhavaan@gmail.com
ADMIN_PASSWORD=your_admin_password

# Email (optional)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# AWS S3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET_NAME=cater-images-prod
AWS_S3_REGION=us-east-1

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Support
If you encounter issues:
1. Check AWS CloudTrail for API errors
2. Verify IAM permissions
3. Check S3 bucket policy
4. Review application logs for detailed error messages

import React, { useState } from 'react';
import { Upload, Progress, Typography, App } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

const { Dragger } = Upload;
const { Text } = Typography;

interface FileUploaderProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // in MB
  onUpload: (file: File, onProgress: (progress: number) => void) => Promise<void>;
  onSuccess?: () => void;
  disabled?: boolean;
  description?: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  accept,
  multiple = true,
  maxSize = 100,
  onUpload,
  onSuccess,
  disabled = false,
  description = 'Click or drag files to this area to upload',
}) => {
  const { message } = App.useApp();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple,
    accept,
    disabled: disabled || uploading,
    beforeUpload: (file) => {
      // Check file size
      const sizeMB = file.size / 1024 / 1024;
      if (sizeMB > maxSize) {
        message.error(`File size must be less than ${maxSize}MB`);
        return Upload.LIST_IGNORE;
      }
      return false; // Prevent auto upload
    },
    customRequest: async ({ file, onProgress: uploadProgress, onSuccess: uploadSuccess, onError }) => {
      setUploading(true);
      setProgress(0);

      try {
        await onUpload(file as File, (prog) => {
          setProgress(prog);
          uploadProgress?.({ percent: prog });
        });
        
        message.success(`${(file as File).name} uploaded successfully`);
        uploadSuccess?.(file);
        onSuccess?.();
        setProgress(0);
      } catch (error: any) {
        message.error(`Upload failed: ${error.detail || error.message}`);
        onError?.(error);
      } finally {
        setUploading(false);
      }
    },
  };

  return (
    <div>
      <Dragger {...uploadProps}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">
          {uploading ? 'Uploading...' : 'Click or drag file to upload'}
        </p>
        <p className="ant-upload-hint">
          {description}
          <br />
          {accept && <Text type="secondary">Accepted formats: {accept}</Text>}
          <br />
          <Text type="secondary">Maximum file size: {maxSize}MB</Text>
        </p>
      </Dragger>
      
      {uploading && (
        <div style={{ marginTop: 16 }}>
          <Progress percent={progress} status="active" />
        </div>
      )}
    </div>
  );
};

export default FileUploader;


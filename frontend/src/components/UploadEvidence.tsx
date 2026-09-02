import React, { useState } from 'react';
import { UploadCloud, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';

interface UploadEvidenceProps {
  projectId: string;
  onSuccess?: () => void;
}

export function UploadEvidence({ projectId, onSuccess }: UploadEvidenceProps) {
  const [file, setFile] = useState<File | null>(null);
  const [stage, setStage] = useState<string>('during');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      // 1. Get presigned URL
      const presignRes = await api.presignUpload({
        project_id: projectId,
        stage: stage,
        filename: file.name,
        content_type: file.type || 'image/jpeg'
      });

      const { upload_url, object_key } = presignRes;

      // 2. PUT file directly to MinIO
      const putRes = await fetch(upload_url, {
        method: 'PUT',
        headers: {
          'Content-Type': file.type || 'image/jpeg'
        },
        body: file
      });

      if (!putRes.ok) {
        throw new Error('Failed to upload file to storage bucket');
      }

      // 3. Complete upload
      await api.completeUpload({
        project_id: projectId,
        stage: stage,
        object_key: object_key
      });

      setSuccess(true);
      setFile(null);
      if (onSuccess) onSuccess();

    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container" style={{ border: '1px dashed #ffffff44', padding: '1.5rem', borderRadius: '8px', marginTop: '1rem', background: 'rgba(0,0,0,0.2)' }}>
      <h3 style={{ marginTop: 0, marginBottom: '1rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <UploadCloud size={20} /> Upload Field Evidence
      </h3>
      
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <select value={stage} onChange={(e) => setStage(e.target.value)} style={{ padding: '0.5rem', borderRadius: '4px', background: 'var(--bg-2)', color: 'white', border: '1px solid #444' }}>
          <option value="before">Before Commencement</option>
          <option value="during">During Construction</option>
          <option value="after">After Completion</option>
          <option value="document">Official Document</option>
        </select>
        
        <input 
          type="file" 
          accept="image/jpeg, image/png, application/pdf"
          onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
          style={{ flex: 1 }}
        />
      </div>

      {error && <div style={{ color: '#ff4d4f', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><AlertTriangle size={16} /> {error}</div>}
      {success && <div style={{ color: '#52c41a', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><CheckCircle size={16} /> Upload successful! Image is being analyzed.</div>}

      <button 
        onClick={handleUpload}
        disabled={!file || uploading}
        style={{ 
          background: file && !uploading ? 'var(--blue)' : '#555',
          color: 'white',
          border: 'none',
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          cursor: file && !uploading ? 'pointer' : 'not-allowed',
          fontWeight: 600
        }}
      >
        {uploading ? 'Uploading...' : 'Submit Evidence'}
      </button>
    </div>
  );
}

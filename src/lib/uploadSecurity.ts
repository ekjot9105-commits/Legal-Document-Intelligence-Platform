export const MAX_UPLOAD_BYTES = 15 * 1024 * 1024
export const SUPPORTED_EXTENSIONS = ['pdf', 'docx', 'txt'] as const

export type UploadValidation =
  | { ok: true; extension: (typeof SUPPORTED_EXTENSIONS)[number] }
  | { ok: false; code: 'unsupported_type' | 'file_too_large' | 'invalid_signature'; message: string }

function extensionFor(filename: string): string {
  return filename.toLowerCase().split('.').pop() ?? ''
}

function hasPrefix(bytes: Uint8Array, prefix: number[]): boolean {
  return prefix.every((value, index) => bytes[index] === value)
}

/** Validate user-selected files before they enter the document processing path. */
export async function validateUploadFile(file: File): Promise<UploadValidation> {
  const extension = extensionFor(file.name)
  if (!SUPPORTED_EXTENSIONS.includes(extension as (typeof SUPPORTED_EXTENSIONS)[number])) {
    return { ok: false, code: 'unsupported_type', message: 'Only PDF, DOCX, and TXT files are supported.' }
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    return { ok: false, code: 'file_too_large', message: 'File exceeds the 15 MB upload limit.' }
  }

  const bytes = new Uint8Array(await file.slice(0, 8).arrayBuffer())
  const signatureValid = extension === 'pdf'
    ? hasPrefix(bytes, [0x25, 0x50, 0x44, 0x46])
    : extension === 'docx'
      ? hasPrefix(bytes, [0x50, 0x4b, 0x03, 0x04])
      : true

  if (!signatureValid) {
    return { ok: false, code: 'invalid_signature', message: 'The file content does not match its declared document type.' }
  }
  return { ok: true, extension: extension as (typeof SUPPORTED_EXTENSIONS)[number] }
}

/** Keep document text clearly separated from assistant instructions at the trust boundary. */
export function isolateDocumentText(text: string): string {
  return `<document_content>\n${text.replaceAll('\u0000', '').slice(0, 200_000)}\n</document_content>`
}

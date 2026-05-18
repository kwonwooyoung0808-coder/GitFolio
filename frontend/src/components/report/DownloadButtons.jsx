import Button from '../common/Button'

export default function DownloadButtons({ reportId, token, pdfAvailable = false, docxAvailable = true }) {
  const base = import.meta.env.VITE_API_BASE_URL

  const download = async (format) => {
    const response = await fetch(`${base}/reports/${reportId}/download?format=${format}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('다운로드에 실패했습니다.')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `gitfolio-report-${reportId}.${format}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-wrap gap-3">
      {pdfAvailable && (
        <Button onClick={() => download('pdf')} className="px-5 py-3">
          PDF 다운로드
        </Button>
      )}
      {docxAvailable && (
        <Button onClick={() => download('docx')} className="bg-sky-700 px-5 py-3 hover:bg-sky-800">
          DOCX 다운로드
        </Button>
      )}
    </div>
  )
}

import axios from 'axios'
import { useCallback, useState } from 'react'

const useMyAxios = <T = unknown>() => {
  const [loading, setLoading] = useState(false)
  const [error, setError]       = useState<any>(null)
  const [data, setData]         = useState<T | null>(null)

  const request = useCallback(
    async (
      url: string,
      method: 'GET' | 'POST' | 'PUT' | 'DELETE',
      body?: any,
      headers?: any
    ) => {
      setLoading(true)
      setError(null)

      try {
        const fullUrl = new URL(url, process.env.NEXT_PUBLIC_BASE_URL).toString()
        const response = await axios({
          url: fullUrl,
          method,
          data: body,
          headers,
          withCredentials: true,  
					credentials: "include",
        })

        setData(response.data)
        return response
      } catch (err) {
        setError(err)
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  return { request, loading, error, data }
}

export default useMyAxios

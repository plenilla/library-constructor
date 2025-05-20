'use client'
import Image, { ImageProps } from "next/image"
import { ComponentProps, useEffect, useState } from 'react'

type ImageWithRefreshProps = ComponentProps<typeof Image> & {
  reloadInterval?: number
}

export default function ImageWithRefresh({
  src,
  alt,
  width,
  height,
  className,
  style,
  fill,
  quality,
  priority,
  loading,
  placeholder,
  blurDataURL,
  unoptimized,
  onLoadingComplete,
  reloadInterval = 3000,
  onClick,
  ...rest
}: ImageWithRefreshProps) {
  const [timestamp, setTimestamp] = useState(Date.now())

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now())
    }, reloadInterval)

    return () => clearInterval(interval)
  }, [reloadInterval])

  const imageSrc = typeof src === 'string' 
    ? `${src}?ts=${timestamp}`
    : src

  return (
    <Image
      {...rest}
      src={imageSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      style={style}
      fill={fill}
      quality={quality}
      priority={priority}
      loading={loading}
      placeholder={placeholder}
      blurDataURL={blurDataURL}
      unoptimized={unoptimized}
      onLoadingComplete={onLoadingComplete}
      onClick={onClick}
    />
  )
}
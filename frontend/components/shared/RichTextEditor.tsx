'use client'

import { Color } from '@tiptap/extension-color'
import FontFamily from '@tiptap/extension-font-family'
import { Image as TiptapImage } from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import TextAlign from '@tiptap/extension-text-align'
import TextStyle from '@tiptap/extension-text-style'
import Typography from '@tiptap/extension-typography'
import Underline from '@tiptap/extension-underline'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from 'next/image'
import { useCallback, useEffect, useState } from 'react'

export const RichTextEditor = ({ content, onChange }) => {
	const [search, setSearch] = useState('')

	const editor = useEditor({
		extensions: [
			StarterKit.configure({ history: true, heading: { levels: [1, 2, 3] } }),
			TextAlign.configure({ types: ['heading', 'paragraph'] }),
			TextStyle.configure({ mergeNestedSpanStyles: true }),
			Color,
			Underline,
			FontFamily,
			Typography,
			TiptapImage.configure({
				inline: true,
			}),
			Link.configure({
				openOnClick: false,
				autolink: true,
				defaultProtocol: 'https',
				protocols: ['http', 'https'],
				isAllowedUri: (url, ctx) => {
					try {
						const parsedUrl = url.includes(':')
							? new URL(url)
							: new URL(`${ctx.defaultProtocol}://${url}`)
						if (!ctx.defaultValidate(parsedUrl.href)) return false
						const disallowed = ['ftp', 'file', 'mailto']
						const proto = parsedUrl.protocol.replace(':', '')
						if (disallowed.includes(proto)) return false
						const allowed = ctx.protocols.map(p =>
							typeof p === 'string' ? p : p.scheme
						)
						if (!allowed.includes(proto)) return false
						const badHosts = ['example-phishing.com', 'malicious-site.net']
						if (badHosts.includes(parsedUrl.hostname)) return false
						return true
					} catch {
						return false
					}
				},
				shouldAutoLink: url => {
					try {
						const parsed = url.includes(':')
							? new URL(url)
							: new URL(`https://${url}`)
						const noAuto = [
							'example-no-autolink.com',
							'another-no-autolink.com',
						]
						return !noAuto.includes(parsed.hostname)
					} catch {
						return false
					}
				},
			}),
		],
		content,
		onUpdate: ({ editor }) => onChange(editor.getHTML()),
	})

	// Ensure setLink hook is called unconditionally
	const setLink = useCallback(() => {
		if (!editor) return
		const prev = editor.getAttributes('link').href
		const url = window.prompt('URL', prev)
		if (url === null) return
		if (url === '') {
			editor.chain().focus().extendMarkRange('link').unsetLink().run()
			return
		}
		try {
			editor
				.chain()
				.focus()
				.extendMarkRange('link')
				.setLink({ href: url })
				.run()
		} catch (e) {
			alert(e.message)
		}
	}, [editor])

	const addImage = useCallback(() => {
		const url = window.prompt('URL')

		if (url) {
			editor.chain().focus().setImage({ src: url }).run()
		}
	}, [editor])

	// Sync external prop changes
	useEffect(() => {
		if (!editor) return
		const current = editor.getHTML()
		if (content !== current) editor.commands.setContent(content)
	}, [content, editor])

	if (!editor) return null

	const currentColor = editor.getAttributes('textStyle').color ?? '#000000'
	const fonts = [
		{ name: 'Inter', value: 'Inter' },
		{ name: 'Comic Sans', value: '"Comic Sans MS", "Comic Sans"' },
		{ name: 'Times New Roman', value: '"Times New Roman", Times, serif' },
		{ name: 'Serif', value: 'serif' },
		{ name: 'Monospace', value: 'monospace' },
		{ name: 'Cursive', value: 'cursive' },
		{ name: 'CSS Variable', value: 'var(--title-font-family)' },
		{ name: 'Exo 2', value: '"Exo 2"' },
	]

	const iconSize = 20
	const canUndo = editor.can().undo()
	const canRedo = editor.can().redo()

	return (
		<>
			<link
				href='https://fonts.googleapis.com/css2?family=Exo+2:ital,wght@0,100..900;1,100..900&display=swap'
				rel='stylesheet'
			/>
			<div className='border rounded p-2'>
				<div className='flex flex-wrap gap-2 mb-2'>
					<div className='flex items-center gap-1'>
						<Image
							src='/icons/color_picker.svg'
							alt='Color Picker'
							width={iconSize}
							height={iconSize}
						/>
						<input
							type='color'
							onInput={e =>
								editor
									.chain()
									.focus()
									.setColor((e.target as HTMLInputElement).value)
									.run()
							}
							value={currentColor}
							data-testid='setColor'
							className='w-5 h-5 p-0 border-0'
						/>
					</div>
					<details
						className='relative group'
						onClick={e => e.stopPropagation()}
					>
						<summary className='cursor-pointer select-none p-2 border rounded w-fit'>
							Шрифт
						</summary>

						<div className='absolute z-10 mt-2 bg-white border rounded shadow p-2 flex flex-col gap-1 max-h-64 overflow-y-auto w-48'>
							<input
								type='text'
								placeholder='Поиск шрифта...'
								className='mb-2 px-2 py-1 border rounded'
								value={search}
								onChange={e => setSearch(e.target.value.toLowerCase())}
							/>

							{fonts
								.filter(font => font.name.toLowerCase().includes(search))
								.map(font => (
									<button
										key={font.name}
										onClick={() =>
											editor?.chain().focus().setFontFamily(font.value).run()
										}
										className={`text-left px-2 py-1 rounded hover:bg-gray-100 ${
											editor?.isActive('textStyle', { fontFamily: font.value })
												? 'bg-gray-200'
												: ''
										}`}
									>
										{font.name}
									</button>
								))}
						</div>
					</details>
					<button
						onClick={() => editor?.chain().focus().unsetFontFamily().run()}
						className='text-left px-2 py-1 rounded hover:bg-red-100 text-red-600'
					>
						Убрать шрифт
					</button>
					{/* Undo */}
					<button
						onClick={() => editor.chain().focus().undo().run()}
						disabled={!canUndo}
						className={`p-1 ${!canUndo ? 'opacity-20 filter grayscale' : ''}`}
					>
						<Image
							src='/icons/undo.svg'
							alt='Undo'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					{/* Redo */}
					<button
						onClick={() => editor.chain().focus().redo().run()}
						disabled={!canRedo}
						className={`p-1 ${!canRedo ? 'opacity-20 filter grayscale' : ''}`}
					>
						<Image
							src='/icons/redo.svg'
							alt='Redo'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button onClick={addImage}>Set image</button>
					<button
						onClick={() => editor.chain().focus().toggleBold().run()}
						className={
							editor.isActive('bold') ? 'bg-gray-200 p-1 rounded' : 'p-1'
						}
					>
						<Image
							src='/icons/bold.svg'
							alt='Bold'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button
						onClick={() => editor.chain().focus().toggleUnderline().run()}
						className={
							editor.isActive('underline') ? 'bg-gray-200 p-1 rounded' : 'p-1'
						}
					>
						<Image
							src='/icons/underline.svg'
							alt='Underline'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button
						onClick={() => editor.chain().focus().setTextAlign('left').run()}
						className={
							editor.isActive({ textAlign: 'left' })
								? 'bg-gray-200 p-1 rounded'
								: 'p-1'
						}
					>
						<Image
							src='/icons/left.svg'
							alt='Align Left'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button
						onClick={() => editor.chain().focus().setTextAlign('center').run()}
						className={
							editor.isActive({ textAlign: 'center' })
								? 'bg-gray-200 p-1 rounded'
								: 'p-1'
						}
					>
						<Image
							src='/icons/center.svg'
							alt='Align Center'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button
						onClick={() => editor.chain().focus().setTextAlign('right').run()}
						className={
							editor.isActive({ textAlign: 'right' })
								? 'bg-gray-200 p-1 rounded'
								: 'p-1'
						}
					>
						<Image
							src='/icons/right.svg'
							alt='Align Right'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button
						onClick={setLink}
						className={
							editor.isActive('link') ? 'bg-gray-200 p-1 rounded' : 'p-1'
						}
					>
						<Image
							src='/icons/add_link.svg'
							alt='Add Link'
							width={iconSize}
							height={iconSize}
						/>
					</button>
					<button
						onClick={() => editor.chain().focus().unsetLink().run()}
						disabled={!editor.isActive('link')}
						className={editor.isActive('link') ? 'p-1' : 'opacity-50 p-1'}
					>
						<Image
							src='/icons/remove_link.svg'
							alt='Remove Link'
							width={iconSize}
							height={iconSize}
						/>
					</button>
				</div>
				<EditorContent
					editor={editor}
					className='min-h-[150px] p-2 prose max-w-none'
				/>
			</div>
		</>
	)
}

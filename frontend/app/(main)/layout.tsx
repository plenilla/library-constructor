import AuthChecker from '@/components/AuthChecker'
import { Footer } from '@/components/shared/Footer'
import { Header } from '@/components/shared/Header'

export default function MainLayout({
	children,
}: {
	children: React.ReactNode
}) {
	return (
		<>
			<AuthChecker />
			<Header />
			<div className='min-h-screen flex flex-col'>
				<main className='flex-1'>{children}</main>
				<Footer className='mt-auto' />
			</div>
		</>
	)
}

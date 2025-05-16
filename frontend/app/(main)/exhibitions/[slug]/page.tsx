import ExhibitionDetail from '@/components/shared/ExhibitionDetail'

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <ExhibitionDetail slug={slug} />;
}
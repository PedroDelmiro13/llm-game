import './globals.css'

export const metadata = {
  title: 'IA de Similaridade em Esportes de Areia',
  description: 'Encontre respostas inteligentes sobre futevôlei, vôlei de praia e esportes relacionados usando busca semântica baseada em IA — resultados relevantes direto de múltiplas fontes.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import Panorama from "@/components/panorama/Panorama";

export const metadata = {
  title: "Panorama nacional — Rota Segura",
  description:
    "Visão geral dos dados de criminalidade do Brasil: ocorrências por estado, evolução, gênero, armas, agentes e drogas.",
};

export default function PaginaPanorama() {
  return (
    <>
      <SiteHeader />
      <main>
        <Panorama />
      </main>
      <SiteFooter />
    </>
  );
}

import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";
import ConsultaIA from "@/components/consulta/ConsultaIA";

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main>
        <ConsultaIA />
      </main>
      <SiteFooter />
    </>
  );
}

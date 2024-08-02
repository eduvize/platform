import { Space, Grid, Button } from "@mantine/core";
import { Hero } from "./Hero";
import { Features } from "./Features";
import { Faq } from "./Faq";
import { Footer } from "./Footer";

export function Home() {
    return (
        <>
            <Hero />
            <Features />
            <Faq />
            <Footer />
        </>
    );
}

import { Card, Container, Grid } from "@mantine/core";
import { InstructorSetup } from "./cta";
import { useInstructor } from "@context/user/hooks";
import { Chat } from "@organisms";
import { ChatProvider } from "@context/chat";
import { useMemo, useRef } from "react";

export const Courses = () => {
    const [instructor] = useInstructor();
    const containerRef = useRef<HTMLDivElement>(null);

    const containerYFromTop = useMemo(() => {
        if (!containerRef.current) return 0;

        return containerRef.current.getBoundingClientRect().top;
    }, [containerRef.current]);

    if (!instructor?.is_approved)
        return (
            <Container ref={containerRef} size="xs">
                <InstructorSetup />
            </Container>
        );

    return (
        <Container size="md" ref={containerRef}>
            <Grid h="100%">
                <Grid.Col span={8}>
                    <ChatProvider>
                        <Chat
                            height={`calc(100vh - ${containerYFromTop}px - 5em)`}
                        />
                    </ChatProvider>
                </Grid.Col>

                <Grid.Col span={4}></Grid.Col>
            </Grid>
        </Container>
    );
};

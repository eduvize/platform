import { Container } from "@mantine/core";
import { InstructorSetup } from "./cta";
import { useInstructor } from "@context/user/hooks";

export const Courses = () => {
    const [instructor] = useInstructor();

    if (!instructor?.is_approved)
        return (
            <Container size="xs">
                <InstructorSetup />
            </Container>
        );

    return <Container size="xl"></Container>;
};

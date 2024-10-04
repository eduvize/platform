import { Button, Group, Stack, Title } from "@mantine/core";
import { Link } from "react-router-dom";

export const Conclusion = () => {
    return (
        <Stack mt="xl">
            <Title ff="Roboto" c="white" ta="center">
                So, what are you waiting for?
            </Title>

            <Group justify="center">
                <Link to="/auth">
                    <Button variant="gradient" size="xl">
                        Create an Account
                    </Button>
                </Link>
            </Group>
        </Stack>
    );
};

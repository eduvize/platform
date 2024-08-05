import {
    Button,
    Paper,
    Text,
    Group,
    CloseButton,
    Divider,
} from "@mantine/core";

export function ResumeBanner() {
    return (
        <Paper radius="md" shadow="md">
            <Group justify="space-between" mb="xs">
                <Text fz="md" fw={500} c="blue">
                    Have a resume?
                </Text>
            </Group>
            <Divider mr="xl" mb="sm" />
            <Text c="dimmed" fz="xs" pr="xl">
                We can automatically process your resume to fill out most of
                your profile if you'd like to save some time. We won't share it
                with anyone, and we don't keep it on our servers.
            </Text>
            <Group justify="flex-start" mt="md">
                <Button variant="default" size="xs">
                    Upload PDF
                </Button>
            </Group>
        </Paper>
    );
}

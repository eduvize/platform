import { Button, Paper, Text, Group, Divider } from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";
import { useRef, useState } from "react";
import FileApi from "../../api/FileApi";
import { ProfileUpdatePayload } from "../../api/contracts";
import { IconCheck } from "@tabler/icons-react";
import { notifications } from "@mantine/notifications";

interface ResumeBannerProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
    onParsing: () => void;
    onCompleted: () => void;
}

export function ResumeBanner({
    form,
    onParsing,
    onCompleted,
}: ResumeBannerProps) {
    const inputRef = useRef<HTMLInputElement>(null);
    const [uploading, setUploading] = useState(false);
    const [wasUploaded, setWasUploaded] = useState(false);

    const handleFileSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        onParsing();
        FileApi.getProfileFromResume(file)
            .then((profile) => {
                form.setValues(profile);
                setWasUploaded(true);

                notifications.show({
                    title: "Resume processed",
                    message:
                        "We've successfully processed your resume. Feel free to make any changes.",
                    color: "blue",
                    autoClose: 8000,
                });
            })
            .catch(() => {
                notifications.show({
                    title: "Failed to process resume",
                    message:
                        "We couldn't process your resume. Please try again or fill out your profile manually.",
                    color: "red",
                    autoClose: 8000,
                });
            })
            .finally(() => {
                setUploading(false);
                onCompleted();
            });
    };

    return (
        <Paper radius="md" shadow="md">
            <input
                type="file"
                ref={inputRef}
                style={{ display: "none" }}
                onChange={handleFileSelection}
                accept=".pdf"
            />

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
                <Button
                    loading={uploading}
                    disabled={uploading || wasUploaded}
                    variant="default"
                    size="xs"
                    leftSection={
                        wasUploaded ? (
                            <IconCheck size={14} color="#2b8a3e" />
                        ) : null
                    }
                    onClick={() => {
                        inputRef.current?.click();
                    }}
                >
                    {wasUploaded ? "Processed!" : "Upload Resume"}
                </Button>
            </Group>
        </Paper>
    );
}

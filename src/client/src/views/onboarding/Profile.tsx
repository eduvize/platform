import { useState, useCallback, useRef, useEffect } from "react";
import { FileApi } from "@api";
import {
    Avatar,
    Button,
    Chip,
    Divider,
    Group,
    Input,
    Pill,
    PillsInput,
    Space,
    Stack,
    Text,
    Title,
} from "@mantine/core";
import { ChatTool, LearningCapacity } from "@models/enums";
import { useOnboardingEvents } from "@context/onboarding/hooks";
import { useDebouncedCallback } from "@mantine/hooks";
import { useToolCallEffect } from "@context/chat";

interface Skill {
    skill_type: number;
    skill: string;
    proficiency: number | null;
}

export const Profile = () => {
    const { sendEvent } = useOnboardingEvents();
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [skills, setSkills] = useState<Skill[]>([]);
    const [disciplines, setDisciplines] = useState<LearningCapacity[]>([]);
    const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
    const [resumeFile, setResumeFile] = useState<File | null>(null);
    const [isUploadingResume, setIsUploadingResume] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const resumeInputRef = useRef<HTMLInputElement>(null);
    const [languageInputValue, setLanguageInputValue] = useState("");
    const [frameworkInputValue, setFrameworkInputValue] = useState("");

    const handleSendLearningCapacityEvent = useDebouncedCallback(() => {
        sendEvent(
            `User has selected their learning disciplines: ${disciplines.join(
                ", "
            )}`
        );
    }, 1500);

    // Handler for discipline selection
    const handleLearningCapacityChange = useCallback(
        (discipline: LearningCapacity) => {
            setDisciplines((prev) => {
                const exists = prev.some((d) => d === discipline);
                if (exists) {
                    return prev.filter((d) => d !== discipline);
                } else {
                    return [...prev, discipline];
                }
            });
            handleSendLearningCapacityEvent();
        },
        []
    );

    // Handler for avatar selection
    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    // Handler for file input change
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file && (file.type === "image/jpeg" || file.type === "image/png")) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setAvatarUrl(e.target?.result as string);
            };
            reader.readAsDataURL(file);

            sendEvent("User uploaded an avatar");
        } else {
            sendEvent("User uploaded an invalid file type for their avatar");
        }
    };

    // Handler for resume upload
    const handleResumeUpload = async () => {
        resumeInputRef.current?.click();
    };

    // Handler for resume file change
    const handleResumeFileChange = async (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        const file = event.target.files?.[0];
        if (file && file.type === "application/pdf") {
            setResumeFile(file);
            setIsUploadingResume(true);
            sendEvent("User is uploading their resume to be processed");
            try {
                const result = await FileApi.getResumeInsights(file);
                sendEvent(
                    `User's resume:\n${result.resume_insights}\n\nUse your tools to incorporate this information in their profile. Ensure you capture all of the information!`
                );
            } catch (error) {
                console.error("Error uploading resume:", error);
            } finally {
                setIsUploadingResume(false);
            }
        }
    };

    const handleProgrammingLanguagesBlur = () => {
        sendEvent(
            `User has updated their programming languages: ${skills
                .map((s) => s.skill)
                .join(", ")}`
        );
    };

    const handleFrameworksBlur = () => {
        sendEvent(
            `User has updated their frameworks or libraries: ${skills
                .map((s) => s.skill)
                .join(", ")}`
        );
    };

    const handleNameBlur = () => {
        if (firstName && lastName) {
            sendEvent(`User has entered their name: ${firstName} ${lastName}`);
        }
    };

    useToolCallEffect(
        ChatTool.ProfileBuilderUpdateProgrammingLanguages,
        (result) => {
            setSkills((prev) => [
                ...prev.filter((v) => v.skill_type !== 1),
                ...result.languages.map((language: string) => ({
                    skill: language,
                    skill_type: 1,
                    proficiency: null,
                })),
            ]);
        }
    );

    useToolCallEffect(ChatTool.ProfileBuilderUpdateLibraries, (result) => {
        setSkills((prev) => [
            ...prev.filter((v) => v.skill_type !== 2),
            ...result.items.map((library: string) => ({
                skill: library,
                skill_type: 2,
                proficiency: null,
            })),
        ]);
    });

    useToolCallEffect(ChatTool.ProfileBuilderSetDisciplines, (result) => {
        const normalizedDisciplines = result.disciplines.map(
            (discipline: string) => {
                switch (discipline) {
                    case "hobbyist":
                        return LearningCapacity.Hobby;
                    case "student":
                        return LearningCapacity.Student;
                    case "professional":
                        return LearningCapacity.Professional;
                    default:
                        return null;
                }
            }
        );
        setDisciplines(normalizedDisciplines.filter((v: any) => v !== null));
    });

    useToolCallEffect(ChatTool.ProfileBuilderSetName, (result) => {
        setFirstName(result.first_name);
        setLastName(result.last_name);
    });

    return (
        <Stack pt="lg" gap="lg">
            <Title order={2} fw={400} c="white">
                Let's Get to Know You.
            </Title>

            <Text c="#C9C9C9" size="sm">
                We need a little information to customize your courses. Chat
                with your Instructor and they'll get all the information they
                need. When they've gathered enough information, click the{" "}
                <b>Next Lesson</b> button to move on to create your first
                Course!
            </Text>

            <Group align="center">
                <Avatar
                    size={128}
                    src={avatarUrl}
                    onClick={handleAvatarClick}
                    styles={{
                        root: {
                            cursor: "pointer",
                        },
                        placeholder: {
                            border: "1px solid #424242",
                            backgroundColor: "transparent",
                        },
                    }}
                />
                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: "none" }}
                    onChange={handleFileChange}
                    accept=".jpg,.jpeg,.png"
                />

                <Group grow style={{ flex: 1 }}>
                    <Stack gap={0} justify="center">
                        <Text>First Name</Text>
                        <Input
                            style={{ width: "100%" }}
                            value={firstName}
                            onChange={(e) =>
                                setFirstName(e.currentTarget.value)
                            }
                            onBlur={handleNameBlur}
                        />
                    </Stack>

                    <Stack gap={0} justify="center">
                        <Text>Last Name</Text>
                        <Input
                            style={{ width: "100%" }}
                            value={lastName}
                            onChange={(e) => setLastName(e.currentTarget.value)}
                            onBlur={handleNameBlur}
                        />
                    </Stack>
                </Group>
            </Group>

            <Stack gap="xs">
                <Title order={4} fw={400} c="white">
                    Your Resume
                </Title>

                <Text c="#C9C9C9" size="sm">
                    We know that a resume is only a snapshot of part of your
                    journey as a developer, but it can be a great starting point
                    for us to get to know you.
                </Text>

                <Group>
                    <Button
                        variant="outline"
                        onClick={handleResumeUpload}
                        disabled={isUploadingResume}
                    >
                        {isUploadingResume ? "Processing..." : "Upload Resume"}
                    </Button>
                    <input
                        type="file"
                        ref={resumeInputRef}
                        style={{ display: "none" }}
                        onChange={handleResumeFileChange}
                        accept=".pdf"
                    />
                </Group>
            </Stack>

            <Divider />

            <Stack gap="xs">
                <Title order={4} fw={400} c="white">
                    Developer Journey
                </Title>

                <Text c="#C9C9C9" size="sm">
                    Tell us a bit about your journey as a developer.
                </Text>

                <Group>
                    <Chip
                        checked={disciplines.includes(LearningCapacity.Hobby)}
                        onClick={() =>
                            handleLearningCapacityChange(LearningCapacity.Hobby)
                        }
                    >
                        I'm a hobbyist
                    </Chip>
                    <Chip
                        checked={disciplines.includes(LearningCapacity.Student)}
                        onClick={() =>
                            handleLearningCapacityChange(
                                LearningCapacity.Student
                            )
                        }
                    >
                        I am or have been a student
                    </Chip>
                    <Chip
                        checked={disciplines.includes(
                            LearningCapacity.Professional
                        )}
                        onClick={() =>
                            handleLearningCapacityChange(
                                LearningCapacity.Professional
                            )
                        }
                    >
                        I'm working in the industry
                    </Chip>
                </Group>
            </Stack>

            <Stack gap="xs">
                <Title order={4} fw={400} c="white">
                    Programming Languages
                </Title>

                <Text c="#C9C9C9" size="sm">
                    What programming languages do you know?
                </Text>

                <PillsInput>
                    <Pill.Group>
                        {skills
                            .filter((v) => v.skill_type === 1)
                            .map((skill) => (
                                <Pill>{skill.skill}</Pill>
                            ))}

                        <PillsInput.Field
                            placeholder="Enter a programming language"
                            value={languageInputValue}
                            onChange={(evt) =>
                                setLanguageInputValue(evt.currentTarget.value)
                            }
                            onKeyDown={(evt) => {
                                if (evt.key === "Enter") {
                                    evt.preventDefault();

                                    setSkills((prev) => [
                                        ...prev,
                                        {
                                            skill: languageInputValue,
                                            skill_type: 1,
                                            proficiency: null,
                                        },
                                    ]);

                                    setLanguageInputValue("");
                                }
                            }}
                            onBlur={handleProgrammingLanguagesBlur}
                        />
                    </Pill.Group>
                </PillsInput>
            </Stack>

            <Stack gap="xs">
                <Title order={4} fw={400} c="white">
                    Frameworks / Libraries
                </Title>

                <Text c="#C9C9C9" size="sm">
                    What libraries or frameworks do you know?
                </Text>

                <PillsInput>
                    <Pill.Group>
                        {skills
                            .filter((v) => v.skill_type === 2)
                            .map((skill) => (
                                <Pill>{skill.skill}</Pill>
                            ))}

                        <PillsInput.Field
                            placeholder="Enter a framework or library"
                            value={frameworkInputValue}
                            onChange={(evt) =>
                                setFrameworkInputValue(evt.currentTarget.value)
                            }
                            onKeyDown={(evt) => {
                                if (evt.key === "Enter") {
                                    evt.preventDefault();

                                    setSkills((prev) => [
                                        ...prev,
                                        {
                                            skill: frameworkInputValue,
                                            skill_type: 2,
                                            proficiency: null,
                                        },
                                    ]);

                                    setFrameworkInputValue("");
                                }
                            }}
                            onBlur={handleFrameworksBlur}
                        />
                    </Pill.Group>
                </PillsInput>
            </Stack>

            <Divider />

            <Group>
                <Button disabled>Next Lesson</Button>
            </Group>

            <Space h="xl" />
        </Stack>
    );
};

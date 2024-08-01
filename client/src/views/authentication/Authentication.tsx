import { useToggle, upperFirst } from "@mantine/hooks";
import { useForm } from "@mantine/form";
import {
    TextInput,
    PasswordInput,
    Text,
    Paper,
    Group,
    PaperProps,
    Button,
    Divider,
    Checkbox,
    Anchor,
    Stack,
    Container,
    Center,
    Space,
} from "@mantine/core";
import { FacebookButton, GoogleButton } from "../../components/atoms";

export const Authentication = (props: PaperProps) => {
    const [type, toggle] = useToggle(["login", "register"]);
    const form = useForm({
        initialValues: {
            email: "",
            name: "",
            password: "",
        },

        validate: {
            email: (val) => (/^\S+@\S+$/.test(val) ? null : "Invalid email"),
            password: (val) =>
                val.length <= 6
                    ? "Password should include at least 6 characters"
                    : null,
        },
    });

    return (
        <Container
            style={{
                height: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}
        >
            <Center>
                <Paper radius="md" p="xl" withBorder {...props}>
                    <Text size="xl" fw={500} style={{ textAlign: "center" }}>
                        Welcome to Eduvize
                    </Text>

                    <Space h="xs" />

                    <Text
                        size="xs"
                        style={{
                            textAlign: "center",
                            color: "var(--mantine-color-dimmed)",
                        }}
                    >
                        {upperFirst(type)} with one of your socials
                    </Text>

                    <Group grow mb="md" mt="md">
                        <GoogleButton radius="xl">Google</GoogleButton>
                        <FacebookButton radius="xl">Facebook</FacebookButton>
                    </Group>

                    <Divider
                        label="Or continue with email"
                        labelPosition="center"
                        my="lg"
                    />

                    <form onSubmit={form.onSubmit(() => {})}>
                        <Stack>
                            <TextInput
                                required
                                label="Email"
                                placeholder="hello@mantine.dev"
                                value={form.values.email}
                                onChange={(event) =>
                                    form.setFieldValue(
                                        "email",
                                        event.currentTarget.value
                                    )
                                }
                                error={form.errors.email && "Invalid email"}
                                radius="md"
                            />

                            {type === "register" && (
                                <TextInput
                                    label="Username"
                                    placeholder="johndoe"
                                    value={form.values.name}
                                    onChange={(event) =>
                                        form.setFieldValue(
                                            "johndoe",
                                            event.currentTarget.value
                                        )
                                    }
                                    radius="md"
                                />
                            )}

                            <PasswordInput
                                required
                                label="Password"
                                placeholder="Your password"
                                value={form.values.password}
                                onChange={(event) =>
                                    form.setFieldValue(
                                        "password",
                                        event.currentTarget.value
                                    )
                                }
                                error={
                                    form.errors.password &&
                                    "Password should include at least 6 characters"
                                }
                                radius="md"
                            />
                        </Stack>

                        <Group justify="space-between" mt="xl">
                            <Anchor
                                component="button"
                                type="button"
                                c="dimmed"
                                onClick={() => toggle()}
                                size="xs"
                            >
                                {type === "register"
                                    ? "Already have an account? Login"
                                    : "Don't have an account? Register"}
                            </Anchor>
                            <Button type="submit" radius="xl">
                                {upperFirst(type)}
                            </Button>
                        </Group>
                    </form>
                </Paper>
            </Center>
        </Container>
    );
};

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
    Anchor,
    Stack,
    Container,
    Center,
    Space,
} from "@mantine/core";
import { FacebookButton, GoogleButton } from "../../components/atoms";
import { Link, useNavigate } from "react-router-dom";
import { useAuthenticated, useLogin, useRegistration } from "../../context";
import { useEffect, useLayoutEffect } from "react";
import { AuthenticationPayload } from "../../api/contracts";

export const Authentication = (props: PaperProps) => {
    const isAuthenticated = useAuthenticated();
    const navigate = useNavigate();
    const [login, loginFailed, resetLogin] = useLogin();
    const [register, registerFailed, resetRegister] = useRegistration();
    const [type, toggle] = useToggle(["login", "register"]);
    const form = useForm<AuthenticationPayload>({
        initialValues: {
            email: "",
            username: "",
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

    useLayoutEffect(() => {
        if (isAuthenticated) {
            navigate("/app");
        }
    });

    useEffect(() => {
        resetLogin();
        resetRegister();
    }, [type]);

    const handleSubmission = (data: AuthenticationPayload) => {
        if (type === "register") {
            register(data.email, data.username as string, data.password);
        } else {
            login(data.email, data.password);
        }
    };

    return (
        <Container
            style={{
                height: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
            }}
        >
            <Center style={{ flexDirection: "column" }}>
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

                    <form
                        onSubmit={form.onSubmit((values) =>
                            handleSubmission(values)
                        )}
                    >
                        <Stack>
                            <TextInput
                                required
                                label="Email"
                                placeholder="you@example.dev"
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
                                    value={form.values.username}
                                    onChange={(event) =>
                                        form.setFieldValue(
                                            "username",
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

                            <Center>
                                <Text inline c="red" size="xs">
                                    {loginFailed && "Invalid email or password"}
                                    {registerFailed &&
                                        "Failed to create an account"}
                                </Text>
                            </Center>
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

                <Link to="/">
                    <Button
                        variant="subtle"
                        style={{ marginTop: "1rem" }}
                        size="xs"
                    >
                        Back to home
                    </Button>
                </Link>
            </Center>
        </Container>
    );
};

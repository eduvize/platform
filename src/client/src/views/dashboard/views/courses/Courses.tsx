import { Avatar, Card } from "@mantine/core";

export const Courses = () => {
    return (
        <div>
            <h1>Courses</h1>

            <Card withBorder>
                <Card.Section p="md">
                    <Avatar
                        size="xl"
                        radius="50%"
                        src="https://oaidalleapiprodscus.blob.core.windows.net/private/org-QF6C4OD5rEGJY3GxKKbe3SSX/user-UrdjT3QojqycIJvqGyrCjeLV/img-CgwM2DnnqJnJk8oqJqPIhw9z.png?st=2024-08-11T20%3A13%3A22Z&se=2024-08-11T22%3A13%3A22Z&sp=r&sv=2023-11-03&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-08-11T06%3A45%3A23Z&ske=2024-08-12T06%3A45%3A23Z&sks=b&skv=2023-11-03&sig=zlUIsp33R//FxKnljn6xj73uQsC4itteaFh1tvwzIo8%3D"
                    />
                </Card.Section>
            </Card>
        </div>
    );
};

import { useChat } from "@context/chat";
import { Avatar, AvatarProps } from "@mantine/core";
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

interface InstructorAvatarProps extends AvatarProps {
    id: string;
}

export const InstructorAvatar = (props: InstructorAvatarProps) => {
    return (
        <Avatar
            {...props}
            src={`${apiEndpoint}/instructors/${props.id}/profile-photo`}
        />
    );
};

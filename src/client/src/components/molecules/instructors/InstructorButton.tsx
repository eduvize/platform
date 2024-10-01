import { Avatar, AvatarProps, UnstyledButton } from "@mantine/core";

interface InstructorButtonProps extends AvatarProps {
    selected?: boolean;
    onSelect?: () => void;
}

export const InstructorButton = ({
    size,
    src,
    selected,
    onSelect,
}: InstructorButtonProps) => {
    return (
        <UnstyledButton
            onClick={() => {
                onSelect?.();
            }}
        >
            <Avatar
                size={size || 128}
                src={src || null}
                style={{
                    border: selected
                        ? "4px solid #8DCAFF"
                        : "2px solid transparent",
                }}
            />
        </UnstyledButton>
    );
};

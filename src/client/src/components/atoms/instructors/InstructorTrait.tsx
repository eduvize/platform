import { Flex, Stepper, Text } from "@mantine/core";

interface InstructorTraitProps {
    name: string;
    value: number;
}

/**
 * InstructorTrait component displays a trait name and its value on a scale of 1-5.
 * @param {InstructorTraitProps} props - The component props
 * @returns {JSX.Element} The rendered InstructorTrait component
 */
export const InstructorTrait = ({ name, value }: InstructorTraitProps) => {
    return (
        <Flex direction="row" gap="md" align="center">
            <Text miw="7em">{name}</Text>

            <Stepper
                orientation="horizontal"
                active={value}
                completedIcon={<></>}
                size="sm"
                styles={{
                    stepIcon: {
                        border: "2px solid #AD5BD7",
                        backgroundColor: "transparent",
                        color: "transparent",
                    },
                    stepCompletedIcon: {
                        border: "none",
                        backgroundColor: "#AD5BD7",
                        borderRadius: "50%",
                    },
                    separator: {
                        backgroundColor: "#AD5BD7",
                        margin: 0,
                        width: "1em",
                    },
                }}
            >
                {[...Array(5)].map((_, index) => (
                    <Stepper.Step key={index} />
                ))}
            </Stepper>
        </Flex>
    );
};

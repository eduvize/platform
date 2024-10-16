import React, { ReactNode } from "react";
import { Stepper, StepperProps, Box, Radio } from "@mantine/core";
import { IconCircleCheckFilled, IconLock } from "@tabler/icons-react";

interface CheckboxStepperProps extends StepperProps {
    children: ReactNode | ReactNode[];
}

/**
 * CheckboxStepper component that renders a vertical stepper with custom styling
 * @param {CheckboxStepperProps} props - The props for the CheckboxStepper component
 * @returns {React.ReactElement} The rendered CheckboxStepper component
 */
export const CheckboxStepper = ({
    children,
    ...props
}: CheckboxStepperProps) => {
    return (
        <Stepper color="green" orientation="vertical" {...props}>
            {React.Children.map(children, (child) => {
                if (
                    React.isValidElement(child) &&
                    child.type === Stepper.Step
                ) {
                    return React.cloneElement(child, {
                        completedIcon: (
                            <Box pos="relative" w={32} h={32} left={-1}>
                                <Box
                                    pos="absolute"
                                    top={8}
                                    left={10}
                                    bg="white"
                                    w={16}
                                    h={16}
                                />
                                <IconCircleCheckFilled
                                    color="#51cf66"
                                    size={36}
                                    style={{
                                        position: "absolute",
                                    }}
                                />
                            </Box>
                        ),
                        progressIcon: (
                            <Radio
                                checked
                                size="lg"
                                variant="outline"
                                styles={{
                                    radio: {
                                        border: "2px solid #51cf66",
                                        background: "transparent",
                                    },
                                    icon: {
                                        color: "#51cf66",
                                    },
                                }}
                            />
                        ),
                        icon: (
                            <Box
                                style={{
                                    border: "1px solid #3d3d3d",
                                    width: 32,
                                    height: 32,
                                    borderRadius: "50%",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                }}
                            >
                                <IconLock size={18} />
                            </Box>
                        ),
                        styles: (theme: any) => ({
                            stepIcon: {
                                padding: 0,
                                backgroundColor: "transparent",
                                borderColor: "transparent",
                            },
                            stepWrapper: {
                                padding: 0,
                            },
                            stepLabel: {
                                fontSize: "0.9rem",
                                fontWeight: 500,
                                color: "#fff",
                            },
                            stepDescription: {
                                fontSize: "0.8rem",
                                color: "#6d6d6d",
                            },
                        }),
                    } as any);
                }
                return child;
            })}
        </Stepper>
    );
};

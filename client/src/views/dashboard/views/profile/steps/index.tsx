export * from "./BasicInfoStep";
export * from "./HobbiesStep";

import { Stepper } from "@mantine/core";
import {
    IconUser,
    IconHammer,
    IconBellSchool,
    IconDeviceLaptop,
    IconReportSearch,
} from "@tabler/icons-react";
import { useEffect, useState } from "react";

interface ProfileStepperProps {
    steps: string[];
    onCanMoveOn: (canMoveOn: boolean) => void;
}

export const ProfileStepper = ({ steps, onCanMoveOn }: ProfileStepperProps) => {
    const [stepIndex, setStepIndex] = useState(0);

    useEffect(() => {
        onCanMoveOn(steps.length > 0 && stepIndex < steps.length - 1);
    }, [steps]);

    return (
        <Stepper
            active={stepIndex}
            orientation="vertical"
            onStepClick={(index) => setStepIndex(index)}
        >
            {steps.includes("basic") && (
                <Stepper.Step
                    key="basic"
                    label="Basic Information"
                    description="Who are you?"
                    icon={<IconUser />}
                />
            )}
            {steps.includes("hobby") && (
                <Stepper.Step
                    key="hobby"
                    label="Hobby Work"
                    description="What do you do for fun?"
                    icon={<IconHammer />}
                />
            )}
            {steps.includes("education") && (
                <Stepper.Step
                    key="education"
                    label="Education"
                    description="Where are you in your studies?"
                    icon={<IconBellSchool />}
                />
            )}
            {steps.includes("employment") && (
                <Stepper.Step
                    key="employment"
                    label="Current Employment"
                    description="What do you do for work?"
                    icon={<IconDeviceLaptop />}
                />
            )}
            {steps.includes("employment") && (
                <Stepper.Step
                    key="experience"
                    label="Professional Experience"
                    description="What have you done in the past?"
                    icon={<IconReportSearch />}
                />
            )}
        </Stepper>
    );
};

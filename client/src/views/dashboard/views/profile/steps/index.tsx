export * from "./BasicInfoStep";
export * from "./HobbiesStep";

import { Stepper } from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";
import {
    IconUser,
    IconHammer,
    IconBellSchool,
    IconDeviceLaptop,
    IconReportSearch,
} from "@tabler/icons-react";
import { useState } from "react";
import { ProfileUpdatePayload } from "../../../../../api/contracts";
import { LearningCapacity } from "../../../../../models/enums";

interface ProfileStepperProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
}

export const ProfileStepper = ({ form }: ProfileStepperProps) => {
    const [stepIndex, setStepIndex] = useState(0);

    return (
        <Stepper
            active={stepIndex}
            orientation="vertical"
            onStepClick={(index) => setStepIndex(index)}
        >
            <Stepper.Step
                key="basic"
                label="General Information"
                description="High-level information about you"
                icon={<IconUser />}
            />
            {form.values.learning_capacities.includes(
                LearningCapacity.Hobby
            ) && (
                <Stepper.Step
                    key="hobby"
                    label="Hobby Work"
                    description="What work you do in your free time"
                    icon={<IconHammer />}
                />
            )}
            {form.values.learning_capacities.includes(
                LearningCapacity.Student
            ) && (
                <Stepper.Step
                    key="education"
                    label="Education"
                    description="Where you're at in your studies"
                    icon={<IconBellSchool />}
                />
            )}
            {form.values.learning_capacities.includes(
                LearningCapacity.Professional
            ) && (
                <>
                    <Stepper.Step
                        key="employment"
                        label="Current Employment"
                        description="What you do right now"
                        icon={<IconDeviceLaptop />}
                    />

                    <Stepper.Step
                        key="experience"
                        label="Professional Experience"
                        description="More about your professional history"
                        icon={<IconReportSearch />}
                    />
                </>
            )}
        </Stepper>
    );
};

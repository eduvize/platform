import { Image, Stepper } from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";
import {
    IconUser,
    IconHammer,
    IconBellSchool,
    IconDeviceLaptop,
    IconStar,
} from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { ProfileUpdatePayload } from "../../api/contracts";
import { LearningCapacity } from "../../models/enums";
import { ProfileStep } from "./Profile";
import { UserDto } from "../../models/dto";

interface ProfileStepperProps {
    userDetails: UserDto | null;
    pendingSave: boolean;
    form: UseFormReturnType<ProfileUpdatePayload>;
    currentStep: ProfileStep;
    disabled?: boolean;
    onChangeStep: (step: ProfileStep) => void;
}

export const ProfileStepper = ({
    userDetails,
    pendingSave,
    form,
    disabled,
    currentStep,
    onChangeStep,
}: ProfileStepperProps) => {
    const steps: ProfileStep[] = [
        "basic",
        "hobby",
        "education",
        "professional",
        "proficiencies",
    ];

    const visibleSteps = useMemo(() => {
        let steps = form.values.learning_capacities.reduce(
            (acc, capacity) => {
                switch (capacity) {
                    case LearningCapacity.Hobby:
                        return acc.concat("hobby");
                    case LearningCapacity.Student:
                        return acc.concat("education");
                    case LearningCapacity.Professional:
                        return acc.concat("professional");
                    default:
                        return acc;
                }
            },
            ["basic"]
        ) as any[];

        if (form.values.skills.length > 0) {
            steps = steps.concat("proficiencies");
        }

        return steps;
    }, [form.values.learning_capacities, form.values.skills]);

    const [stepIndex, setStepIndex] = useState(steps.indexOf(currentStep));

    useEffect(() => {
        onChangeStep(visibleSteps[stepIndex]);
    }, [stepIndex]);

    useEffect(() => {
        if (stepIndex === visibleSteps.indexOf(currentStep)) return;

        console.log("currentStep", currentStep);
        setStepIndex(visibleSteps.indexOf(currentStep));
    }, [currentStep, visibleSteps]);

    const getStepProps = (step: ProfileStep) => ({
        styles: {
            stepIcon: {
                border:
                    currentStep === step
                        ? "2px solid var(--mantine-color-blue-text)"
                        : undefined,
            },
        },
        loading: currentStep === step && pendingSave,
        disabled: disabled,
    });

    return (
        <Stepper
            allowNextStepsSelect={false}
            active={stepIndex}
            orientation="vertical"
            onStepClick={(index) => setStepIndex(index)}
        >
            <Stepper.Step
                {...getStepProps("basic")}
                key="basic"
                label="General Information"
                description="The basics about you"
                completedIcon={
                    userDetails?.profile?.avatar_url ? (
                        <Image
                            src={userDetails.profile.avatar_url}
                            radius="50%"
                        />
                    ) : (
                        <IconUser />
                    )
                }
                icon={<IconUser />}
            />
            {visibleSteps.includes("hobby") && (
                <Stepper.Step
                    {...getStepProps("hobby")}
                    key="hobby"
                    label="Personal Projects"
                    description="What you do in your free time"
                    icon={<IconHammer />}
                />
            )}
            {visibleSteps.includes("education") && (
                <Stepper.Step
                    {...getStepProps("education")}
                    key="education"
                    label="Education"
                    description="Academic background and certifications"
                    icon={<IconBellSchool />}
                />
            )}
            {visibleSteps.includes("professional") && (
                <Stepper.Step
                    {...getStepProps("professional")}
                    key="professional"
                    label="Professional Experience"
                    description="What you've done in the workforce"
                    icon={<IconDeviceLaptop />}
                />
            )}
            {visibleSteps.includes("proficiencies") && (
                <Stepper.Step
                    {...getStepProps("proficiencies")}
                    key="proficiencies"
                    label="Proficiencies"
                    description="How you view your skills"
                    icon={<IconStar />}
                />
            )}
        </Stepper>
    );
};

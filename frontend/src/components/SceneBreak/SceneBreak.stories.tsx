import type { Meta, StoryObj } from "@storybook/react";
import { SceneBreak } from ".";

const meta: Meta<typeof SceneBreak> = {
  title: "Molecules/SceneBreak",
  component: SceneBreak,
  parameters: { layout: "padded" },
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div style={{ maxWidth: "720px", fontFamily: "Georgia, serif", fontSize: "18px" }}>
        <p style={{ color: "var(--color-text-primary)" }}>
          Der Morgen begann ruhig. Licht fiel durch die Jalousien.
        </p>
        <Story />
        <p style={{ color: "var(--color-text-primary)" }}>
          Die Stille dauerte nicht lange. Schon bald klopfte jemand an die Tür.
        </p>
      </div>
    ),
  ],
};
export default meta;
type Story = StoryObj<typeof SceneBreak>;

export const Default: Story = {
  args: { title: "Szene 1" },
};

export const LongTitle: Story = {
  args: { title: "Die Verhandlung im Bundesministerium" },
};

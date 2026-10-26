plugins {
    java
    // Not bound to a lifecycle task. qestack calls the 'pitest' task directly.
    id("info.solidsoft.pitest") version "1.19.0"
}

repositories {
    mavenCentral()
}

// Compile for Java 17 with the JDK that runs Gradle (no toolchain download needed).
tasks.withType<JavaCompile>().configureEach {
    options.release = 17
}

testing {
    suites {
        getByName<JvmTestSuite>("test") {
            useJUnitJupiter("5.14.4")
            dependencies {
                implementation("org.assertj:assertj-core:3.27.7")
            }
        }
        // Container-based tests (*IT) live in src/integrationTest/java.
        register<JvmTestSuite>("integrationTest") {
            useJUnitJupiter("5.14.4")
            dependencies {
                implementation(project())
                implementation("org.assertj:assertj-core:3.27.7")
            }
            targets.all {
                testTask.configure { shouldRunAfter("test") }
            }
        }
    }
}

// qestack passes -Pqe.groups=feature-NNN. Empty or missing means: run all tests.
val qeGroups = providers.gradleProperty("qe.groups").orElse("")

tasks.withType<Test>().configureEach {
    useJUnitPlatform {
        if (qeGroups.get().isNotBlank()) includeTags(qeGroups.get())
    }
    // The gate tool reads the XML reports, not the exit code: a red test must not stop the build.
    ignoreFailures = true
    // Gradle passes -D from the command line to the build JVM, not to the test JVM.
    // Forward the JUnit settings that qestack sets as -Pjunit.* (random order and seed).
    providers.gradlePropertiesPrefixedBy("junit.").get().forEach { (key, value) -> systemProperty(key, value) }
    // The test task is up to date after a run. qestack must run the tests each time.
    outputs.upToDateWhen { false }
}

pitest {
    junit5PluginVersion = "1.2.3"
    pitestVersion = "1.30.1"
    mutators = setOf("STRONGER")
    outputFormats = setOf("XML", "HTML")
    timestampedReports = false
    threads = 4
    timeoutConstInMillis = 8000
    failWhenNoMutations = false
    // Exclude the slow container tests. Seeded faults measure them instead.
    excludedGroups = setOf("integration", "ui")
    // qestack sets these for each run (class patterns, comma separated).
    providers.gradleProperty("qe.targetClasses").orNull?.let { targetClasses = it.split(",").toSet() }
    providers.gradleProperty("qe.targetTests").orNull?.let { targetTests = it.split(",").toSet() }
}

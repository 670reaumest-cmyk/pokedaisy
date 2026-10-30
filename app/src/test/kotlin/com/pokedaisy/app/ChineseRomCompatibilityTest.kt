package com.pokedaisy.app

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** Regression checks for Chinese ROM filenames and UTF-8 archives.
 * Actual Chinese ROM-hack memory mappings still require device testing.
 */
class ChineseRomCompatibilityTest {
    @Test fun chineseFileNamesRemainUnchanged() {
        assertEquals("宝可梦·漆黑的魅影.gba", RomUris.sanitizeFileName("宝可梦·漆黑的魅影.gba"))
        assertEquals("精灵宝可梦 心金.nds", RomUris.sanitizeFileName(" 精灵宝可梦 心金.nds "))
        assertEquals("口袋妖怪_水晶.gbc", RomUris.sanitizeFileName("口袋妖怪_水晶.gbc"))
    }
    @Test fun chineseNamedGbaHeaderRemainsReadable() {
        val dir = createTempDir(prefix = "中文ROM测试_")
        try {
            val rom = File(dir, "宝可梦-火红（汉化）.gba")
            val bytes = ByteArray(4096)
            "BPRE".toByteArray(Charsets.US_ASCII).copyInto(bytes, destinationOffset = 0xAC)
            bytes[0xB2] = 0x96.toByte()
            rom.writeBytes(bytes)
            assertEquals("BPRE", RomIdentity.gameCode(rom))
            assertTrue(RomIdentity.looksLikeRom(rom))
            assertEquals("宝可梦-火红（汉化）", RomArchive.baseName(rom))
        } finally { dir.deleteRecursively() }
    }
    @Test fun unicodeZipRomEntryAndSaveBaseNameWork() {
        val dir = createTempDir(prefix = "中文ZIP测试_")
        try {
            val archive = File(dir, "我的中文宝可梦.zip")
            val bytes = ByteArray(4096)
            "BPEE".toByteArray(Charsets.US_ASCII).copyInto(bytes, destinationOffset = 0xAC)
            bytes[0xB2] = 0x96.toByte()
            ZipOutputStream(archive.outputStream()).use { zip ->
                zip.putNextEntry(ZipEntry("中文补丁/绿宝石（简体中文）.gba"))
                zip.write(bytes)
                zip.closeEntry()
            }
            assertEquals("中文补丁/绿宝石（简体中文）.gba", RomArchive.romEntry(archive)?.name)
            assertEquals("绿宝石（简体中文）", RomArchive.baseName(archive))
            assertEquals("BPEE", RomIdentity.gameCode(archive))
            assertTrue(RomIdentity.looksLikeRom(archive))
        } finally { dir.deleteRecursively() }
    }
}
